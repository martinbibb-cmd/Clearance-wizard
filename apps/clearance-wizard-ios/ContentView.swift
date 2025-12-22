//
//  ContentView.swift
//  Clearance Wizard
//
//  Main SwiftUI view showing live AR camera with marker detection
//

import SwiftUI
import ARKit

struct ContentView: View {
    @StateObject private var arManager = ARManager()
    @State private var showingInfo = false
    
    var body: some View {
        ZStack {
            // AR Camera View
            ARViewContainer(arManager: arManager)
                .edgesIgnoringSafeArea(.all)
            
            // Overlay UI
            VStack {
                // Top bar
                HStack {
                    Text("Clearance Wizard")
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding(8)
                        .background(Color.black.opacity(0.7))
                        .cornerRadius(8)
                    
                    Spacer()
                    
                    Button(action: {
                        showingInfo.toggle()
                    }) {
                        Image(systemName: "info.circle")
                            .font(.title2)
                            .foregroundColor(.white)
                            .padding(8)
                            .background(Color.black.opacity(0.7))
                            .cornerRadius(8)
                    }
                }
                .padding()
                
                Spacer()
                
                // Detection Status
                VStack(spacing: 8) {
                    if let markerInfo = arManager.detectedMarkerInfo {
                        HStack {
                            Image(systemName: "checkmark.circle.fill")
                                .foregroundColor(.green)
                            Text("Marker Detected")
                                .font(.subheadline)
                                .foregroundColor(.white)
                        }
                        .padding(8)
                        .background(Color.black.opacity(0.7))
                        .cornerRadius(8)
                        
                        Text(markerInfo)
                            .font(.caption)
                            .foregroundColor(.white)
                            .padding(8)
                            .background(Color.black.opacity(0.7))
                            .cornerRadius(8)
                    } else {
                        HStack {
                            ProgressView()
                                .progressViewStyle(CircularProgressViewStyle(tint: .white))
                            Text("Scanning for markers...")
                                .font(.subheadline)
                                .foregroundColor(.white)
                        }
                        .padding(8)
                        .background(Color.black.opacity(0.7))
                        .cornerRadius(8)
                    }
                    
                    // Anchor count
                    if arManager.anchorCount > 0 {
                        Text("\(arManager.anchorCount) anchor(s) placed")
                            .font(.caption)
                            .foregroundColor(.white)
                            .padding(8)
                            .background(Color.blue.opacity(0.7))
                            .cornerRadius(8)
                    }
                }
                .padding(.bottom, 40)
            }
        }
        .alert("About", isPresented: $showingInfo) {
            Button("OK", role: .cancel) { }
        } message: {
            Text("""
            Clearance Wizard AR Starter
            
            This app demonstrates:
            • Live AR camera view
            • QR code marker detection (MVP)
            • Raycast-based anchor placement
            • Stable tracking with ARTrackedRaycast
            
            Point your camera at a QR code to detect it and place an anchor.
            """)
        }
    }
}

// MARK: - AR Manager
class ARManager: ObservableObject {
    @Published var detectedMarkerInfo: String?
    @Published var anchorCount: Int = 0
    
    func updateMarkerDetection(info: String?) {
        DispatchQueue.main.async {
            self.detectedMarkerInfo = info
        }
    }
    
    func updateAnchorCount(_ count: Int) {
        DispatchQueue.main.async {
            self.anchorCount = count
        }
    }
}

#Preview {
    ContentView()
}
