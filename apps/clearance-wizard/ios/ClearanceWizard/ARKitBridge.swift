//
//  ARKitBridge.swift
//  ClearanceWizard
//
//  Swift ARKit native module for React Native
//  Provides stable AR tracking, anchors, and measurements
//

import Foundation
import ARKit
import SceneKit

@objc(ARKitBridge)
class ARKitBridge: RCTEventEmitter, ARSessionDelegate {
    
    private var arSession: ARSession?
    private var configuration: ARWorldTrackingConfiguration?
    private var anchors: [String: ARAnchor] = [:]
    private var hasListeners = false
    
    // MARK: - Module Setup
    
    override init() {
        super.init()
        setupARSession()
    }
    
    private func setupARSession() {
        arSession = ARSession()
        arSession?.delegate = self
        configuration = ARWorldTrackingConfiguration()
        configuration?.planeDetection = [.horizontal, .vertical]
        configuration?.isLightEstimationEnabled = true
    }
    
    override static func requiresMainQueueSetup() -> Bool {
        return true
    }
    
    override func supportedEvents() -> [String]! {
        return ["onFrame", "onAnchorUpdate", "onError"]
    }
    
    override func startObserving() {
        hasListeners = true
    }
    
    override func stopObserving() {
        hasListeners = false
    }
    
    // MARK: - Public API Methods
    
    @objc
    func startSession(_ resolve: @escaping RCTPromiseResolveBlock,
                     rejecter reject: @escaping RCTPromiseRejectBlock) {
        DispatchQueue.main.async { [weak self] in
            guard let self = self else {
                reject("ERROR", "Module deallocated", nil)
                return
            }
            
            guard ARWorldTrackingConfiguration.isSupported else {
                reject("NOT_SUPPORTED", "ARKit is not supported on this device", nil)
                return
            }
            
            guard let config = self.configuration else {
                reject("CONFIG_ERROR", "Configuration not initialized", nil)
                return
            }
            
            self.arSession?.run(config, options: [.resetTracking, .removeExistingAnchors])
            resolve(["success": true])
        }
    }
    
    @objc
    func stopSession(_ resolve: @escaping RCTPromiseResolveBlock,
                    rejecter reject: @escaping RCTPromiseRejectBlock) {
        DispatchQueue.main.async { [weak self] in
            self?.arSession?.pause()
            self?.anchors.removeAll()
            resolve(["success": true])
        }
    }
    
    @objc
    func hitTest(_ x: NSNumber,
                y: NSNumber,
                resolver resolve: @escaping RCTPromiseResolveBlock,
                rejecter reject: @escaping RCTPromiseRejectBlock) {
        DispatchQueue.main.async { [weak self] in
            guard let frame = self?.arSession?.currentFrame else {
                reject("NO_FRAME", "No current AR frame available", nil)
                return
            }
            
            let point = CGPoint(x: x.doubleValue, y: y.doubleValue)
            let results = frame.hitTest(point, types: [.existingPlaneUsingExtent, .estimatedHorizontalPlane])
            
            if let result = results.first {
                let transform = result.worldTransform
                let planeDetected = result.type == .existingPlaneUsingExtent
                
                resolve([
                    "worldTransform": self?.matrixToArray(transform) ?? [],
                    "planeDetected": planeDetected,
                    "confidence": planeDetected ? 1.0 : 0.7
                ])
            } else {
                reject("NO_HIT", "No surface detected at point", nil)
            }
        }
    }
    
    @objc
    func createAnchor(_ transformArray: [NSNumber],
                     resolver resolve: @escaping RCTPromiseResolveBlock,
                     rejecter reject: @escaping RCTPromiseRejectBlock) {
        DispatchQueue.main.async { [weak self] in
            guard let self = self else {
                reject("ERROR", "Module deallocated", nil)
                return
            }
            
            let transform = self.arrayToMatrix(transformArray)
            let anchor = ARAnchor(transform: transform)
            let anchorId = anchor.identifier.uuidString
            
            self.anchors[anchorId] = anchor
            self.arSession?.add(anchor: anchor)
            
            resolve([
                "anchorId": anchorId,
                "transform": transformArray
            ])
        }
    }
    
    @objc
    func getTrackingState(_ resolve: @escaping RCTPromiseResolveBlock,
                         rejecter reject: @escaping RCTPromiseRejectBlock) {
        DispatchQueue.main.async { [weak self] in
            guard let frame = self?.arSession?.currentFrame else {
                reject("NO_FRAME", "No current AR frame available", nil)
                return
            }
            
            let state = self?.trackingStateToString(frame.camera.trackingState) ?? "notAvailable"
            let reason = self?.trackingStateReasonToString(frame.camera.trackingStateReason) ?? "none"
            
            resolve([
                "state": state,
                "reason": reason
            ])
        }
    }
    
    @objc
    func measureRay(_ x1: NSNumber, y1: NSNumber,
                   x2: NSNumber, y2: NSNumber,
                   resolver resolve: @escaping RCTPromiseResolveBlock,
                   rejecter reject: @escaping RCTPromiseRejectBlock) {
        DispatchQueue.main.async { [weak self] in
            guard let frame = self?.arSession?.currentFrame else {
                reject("NO_FRAME", "No current AR frame available", nil)
                return
            }
            
            let point1 = CGPoint(x: x1.doubleValue, y: y1.doubleValue)
            let point2 = CGPoint(x: x2.doubleValue, y: y2.doubleValue)
            
            let results1 = frame.hitTest(point1, types: [.existingPlaneUsingExtent, .featurePoint])
            let results2 = frame.hitTest(point2, types: [.existingPlaneUsingExtent, .featurePoint])
            
            guard let hit1 = results1.first, let hit2 = results2.first else {
                reject("NO_HIT", "Could not detect surfaces at both points", nil)
                return
            }
            
            let pos1 = SCNVector3(hit1.worldTransform.columns.3.x,
                                 hit1.worldTransform.columns.3.y,
                                 hit1.worldTransform.columns.3.z)
            let pos2 = SCNVector3(hit2.worldTransform.columns.3.x,
                                 hit2.worldTransform.columns.3.y,
                                 hit2.worldTransform.columns.3.z)
            
            let distance = self?.distance(from: pos1, to: pos2) ?? 0
            let distanceMm = distance * 1000.0 // Convert to mm
            
            let confidence = min(
                hit1.type == .existingPlaneUsingExtent ? 1.0 : 0.7,
                hit2.type == .existingPlaneUsingExtent ? 1.0 : 0.7
            )
            
            resolve([
                "distanceMm": distanceMm,
                "pointA": ["x": pos1.x, "y": pos1.y, "z": pos1.z],
                "pointB": ["x": pos2.x, "y": pos2.y, "z": pos2.z],
                "confidence": confidence
            ])
        }
    }
    
    @objc
    func capturePhoto(_ resolve: @escaping RCTPromiseResolveBlock,
                     rejecter reject: @escaping RCTPromiseRejectBlock) {
        DispatchQueue.main.async { [weak self] in
            guard let frame = self?.arSession?.currentFrame else {
                reject("NO_FRAME", "No current AR frame available", nil)
                return
            }
            
            let pixelBuffer = frame.capturedImage
            let ciImage = CIImage(cvPixelBuffer: pixelBuffer)
            let context = CIContext()
            
            guard let cgImage = context.createCGImage(ciImage, from: ciImage.extent) else {
                reject("CAPTURE_ERROR", "Failed to create image", nil)
                return
            }
            
            let image = UIImage(cgImage: cgImage)
            
            // Save to temporary directory
            let timestamp = Int(Date().timeIntervalSince1970 * 1000)
            let filename = "capture_\(timestamp).jpg"
            let tempDir = NSTemporaryDirectory()
            let filePath = (tempDir as NSString).appendingPathComponent(filename)
            
            guard let imageData = image.jpegData(compressionQuality: 0.9),
                  (try? imageData.write(to: URL(fileURLWithPath: filePath))) != nil else {
                reject("SAVE_ERROR", "Failed to save image", nil)
                return
            }
            
            resolve([
                "localPath": filePath,
                "width": Int(image.size.width),
                "height": Int(image.size.height)
            ])
        }
    }
    
    // MARK: - ARSessionDelegate
    
    func session(_ session: ARSession, didUpdate frame: ARFrame) {
        guard hasListeners else { return }
        
        let camera = frame.camera
        let intrinsics = camera.intrinsics
        let transform = camera.transform
        
        sendEvent(withName: "onFrame", body: [
            "intrinsics": [
                "fx": intrinsics[0][0],
                "fy": intrinsics[1][1],
                "cx": intrinsics[2][0],
                "cy": intrinsics[2][1],
                "width": frame.camera.imageResolution.width,
                "height": frame.camera.imageResolution.height
            ],
            "cameraTransform": matrixToArray(transform),
            "trackingState": trackingStateToString(camera.trackingState),
            "timestamp": Int(Date().timeIntervalSince1970 * 1000)
        ])
    }
    
    func session(_ session: ARSession, didAdd anchors: [ARAnchor]) {
        guard hasListeners else { return }
        
        for anchor in anchors {
            sendEvent(withName: "onAnchorUpdate", body: [
                "anchorId": anchor.identifier.uuidString,
                "transform": matrixToArray(anchor.transform),
                "type": "added"
            ])
        }
    }
    
    func session(_ session: ARSession, didUpdate anchors: [ARAnchor]) {
        guard hasListeners else { return }
        
        for anchor in anchors {
            sendEvent(withName: "onAnchorUpdate", body: [
                "anchorId": anchor.identifier.uuidString,
                "transform": matrixToArray(anchor.transform),
                "type": "updated"
            ])
        }
    }
    
    func session(_ session: ARSession, didFailWithError error: Error) {
        guard hasListeners else { return }
        
        sendEvent(withName: "onError", body: [
            "code": "SESSION_ERROR",
            "message": error.localizedDescription
        ])
    }
    
    // MARK: - Helper Methods
    
    private func matrixToArray(_ matrix: simd_float4x4) -> [Float] {
        return [
            matrix.columns.0.x, matrix.columns.0.y, matrix.columns.0.z, matrix.columns.0.w,
            matrix.columns.1.x, matrix.columns.1.y, matrix.columns.1.z, matrix.columns.1.w,
            matrix.columns.2.x, matrix.columns.2.y, matrix.columns.2.z, matrix.columns.2.w,
            matrix.columns.3.x, matrix.columns.3.y, matrix.columns.3.z, matrix.columns.3.w
        ]
    }
    
    private func arrayToMatrix(_ array: [NSNumber]) -> simd_float4x4 {
        let floats = array.map { $0.floatValue }
        return simd_float4x4(
            SIMD4<Float>(floats[0], floats[1], floats[2], floats[3]),
            SIMD4<Float>(floats[4], floats[5], floats[6], floats[7]),
            SIMD4<Float>(floats[8], floats[9], floats[10], floats[11]),
            SIMD4<Float>(floats[12], floats[13], floats[14], floats[15])
        )
    }
    
    private func distance(from: SCNVector3, to: SCNVector3) -> Float {
        let dx = to.x - from.x
        let dy = to.y - from.y
        let dz = to.z - from.z
        return sqrt(dx*dx + dy*dy + dz*dz)
    }
    
    private func trackingStateToString(_ state: ARCamera.TrackingState) -> String {
        switch state {
        case .notAvailable:
            return "notAvailable"
        case .limited:
            return "limited"
        case .normal:
            return "normal"
        }
    }
    
    private func trackingStateReasonToString(_ reason: ARCamera.TrackingState.Reason) -> String {
        switch reason {
        case .initializing:
            return "initializing"
        case .excessiveMotion:
            return "excessiveMotion"
        case .insufficientFeatures:
            return "insufficientFeatures"
        case .relocalizing:
            return "relocalizing"
        default:
            return "none"
        }
    }
}
