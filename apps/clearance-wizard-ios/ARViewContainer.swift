//
//  ARViewContainer.swift
//  Clearance Wizard
//
//  ARKit + Vision integration for marker detection and anchor placement
//

import SwiftUI
import ARKit
import RealityKit
import Vision

struct ARViewContainer: UIViewRepresentable {
    let arManager: ARManager
    
    func makeUIView(context: Context) -> ARView {
        let arView = ARView(frame: .zero)
        
        // Configure AR session
        let config = ARWorldTrackingConfiguration()
        config.planeDetection = [.horizontal, .vertical]
        config.isLightEstimationEnabled = true
        arView.session.run(config)
        
        // Set up coordinator as delegate
        context.coordinator.arView = arView
        arView.session.delegate = context.coordinator
        
        // Add debug options for development
        #if DEBUG
        arView.debugOptions = [.showFeaturePoints, .showWorldOrigin]
        #endif
        
        return arView
    }
    
    func updateUIView(_ uiView: ARView, context: Context) {
        // Updates handled by coordinator
    }
    
    func makeCoordinator() -> Coordinator {
        Coordinator(arManager: arManager)
    }
    
    // MARK: - Coordinator
    class Coordinator: NSObject, ARSessionDelegate {
        let arManager: ARManager
        weak var arView: ARView?
        
        private let visionQueue = DispatchQueue(label: "com.clearancewizard.vision")
        private var lastDetectionTime: Date = .distantPast
        private let detectionThrottle: TimeInterval = 0.5 // Process every 0.5 seconds
        
        // Track anchors
        private var trackedRaycast: ARTrackedRaycast?
        private var markerAnchors: [ARAnchor] = []
        
        init(arManager: ARManager) {
            self.arManager = arManager
            super.init()
        }
        
        // MARK: - ARSessionDelegate
        
        func session(_ session: ARSession, didUpdate frame: ARFrame) {
            // Throttle detection to avoid performance issues
            let now = Date()
            guard now.timeIntervalSince(lastDetectionTime) >= detectionThrottle else {
                return
            }
            lastDetectionTime = now
            
            // Run QR detection on background queue
            let pixelBuffer = frame.capturedImage
            visionQueue.async { [weak self] in
                self?.detectQRCodes(in: pixelBuffer, frame: frame)
            }
        }
        
        // MARK: - QR Code Detection with Vision
        
        private func detectQRCodes(in pixelBuffer: CVPixelBuffer, frame: ARFrame) {
            let request = VNDetectBarcodesRequest { [weak self] request, error in
                guard let self = self else { return }
                
                if let error = error {
                    print("QR Detection error: \(error.localizedDescription)")
                    return
                }
                
                guard let results = request.results as? [VNBarcodeObservation],
                      let firstQR = results.first else {
                    DispatchQueue.main.async {
                        self.arManager.updateMarkerDetection(info: nil)
                    }
                    return
                }
                
                // QR code detected!
                let payload = firstQR.payloadStringValue ?? "Unknown"
                let confidence = firstQR.confidence
                
                DispatchQueue.main.async {
                    self.arManager.updateMarkerDetection(
                        info: "QR: \(payload) (conf: \(String(format: "%.2f", confidence)))"
                    )
                }
                
                // Calculate center of QR code in normalized coordinates
                let bounds = firstQR.boundingBox
                let centerX = bounds.midX
                let centerY = bounds.midY
                
                // Vision coordinates are normalized [0,1] with origin at bottom-left
                // Convert to ARKit screen space (origin at top-left)
                let screenCenter = CGPoint(
                    x: centerX,
                    y: 1.0 - centerY
                )
                
                // Perform raycast from marker center
                self.performRaycast(at: screenCenter, frame: frame, markerInfo: payload)
            }
            
            // Configure to detect QR codes
            request.symbologies = [.qr]
            
            let handler = VNImageRequestHandler(cvPixelBuffer: pixelBuffer, options: [:])
            do {
                try handler.perform([request])
            } catch {
                print("Failed to perform QR detection: \(error)")
            }
        }
        
        // MARK: - Raycast & Anchor Placement
        
        private func performRaycast(at normalizedPoint: CGPoint, frame: ARFrame, markerInfo: String) {
            guard let arView = arView else { return }
            
            // Convert normalized point to view coordinates
            let viewSize = arView.bounds.size
            let viewPoint = CGPoint(
                x: normalizedPoint.x * viewSize.width,
                y: normalizedPoint.y * viewSize.height
            )
            
            // Create raycast query
            guard let query = arView.makeRaycastQuery(
                from: viewPoint,
                allowing: .existingPlaneGeometry,
                alignment: .any
            ) else {
                // Fallback: try estimatedPlane if no existing plane found
                if let query = arView.makeRaycastQuery(
                    from: viewPoint,
                    allowing: .estimatedPlane,
                    alignment: .any
                ) {
                    performRaycastWithQuery(query, markerInfo: markerInfo)
                }
                return
            }
            
            performRaycastWithQuery(query, markerInfo: markerInfo)
        }
        
        private func performRaycastWithQuery(_ query: ARRaycastQuery, markerInfo: String) {
            guard let arView = arView else { return }
            
            // If we already have a tracked raycast, update it
            if let existingRaycast = trackedRaycast {
                // Update existing raycast
                existingRaycast.stopTracking()
                trackedRaycast = nil
            }
            
            // Create new tracked raycast for continuous updates
            trackedRaycast = arView.session.trackedRaycast(query) { [weak self] results in
                guard let self = self,
                      let result = results.first else {
                    return
                }
                
                self.updateAnchor(with: result, markerInfo: markerInfo)
            }
        }
        
        private func updateAnchor(with result: ARRaycastResult, markerInfo: String) {
            guard let arView = arView else { return }
            
            // Remove old anchors (keep only most recent)
            for anchor in markerAnchors {
                arView.session.remove(anchor: anchor)
            }
            markerAnchors.removeAll()
            
            // Create new anchor at raycast hit location
            let anchor = ARAnchor(name: "QR-\(markerInfo)", transform: result.worldTransform)
            arView.session.add(anchor: anchor)
            markerAnchors.append(anchor)
            
            // Create visual indicator (simple box)
            createVisualIndicator(at: result.worldTransform)
            
            // Update anchor count
            DispatchQueue.main.async {
                self.arManager.updateAnchorCount(self.markerAnchors.count)
            }
        }
        
        private func createVisualIndicator(at transform: simd_float4x4) {
            guard let arView = arView else { return }
            
            // Remove existing indicator entities
            arView.scene.anchors.forEach { anchor in
                if anchor.name.hasPrefix("indicator-") {
                    arView.scene.removeAnchor(anchor)
                }
            }
            
            // Create a simple box mesh
            let mesh = MeshResource.generateBox(size: [0.1, 0.1, 0.1])
            
            // Create material with semi-transparent blue color
            var material = SimpleMaterial()
            material.color = .init(tint: .blue.withAlphaComponent(0.7), texture: nil)
            
            // Create model entity
            let modelEntity = ModelEntity(mesh: mesh, materials: [material])
            
            // Create anchor entity at the transform location
            let anchorEntity = AnchorEntity(world: transform)
            anchorEntity.name = "indicator-marker"
            anchorEntity.addChild(modelEntity)
            
            // Add to scene
            arView.scene.addAnchor(anchorEntity)
        }
    }
}
