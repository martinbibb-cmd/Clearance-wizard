# Quick Setup Guide - Clearance Wizard iOS

## Step-by-Step: Creating the Xcode Project

### 1. Create New Xcode Project

1. Open **Xcode** (version 15.0 or later)
2. Select **File → New → Project**
3. Choose **iOS** tab at the top
4. Select **App** template
5. Click **Next**

### 2. Configure Project Settings

Fill in the project details:

| Field | Value |
|-------|-------|
| **Product Name** | Clearance Wizard |
| **Team** | Select your team or leave as "None" |
| **Organization Identifier** | com.clearancewizard (or your preference) |
| **Bundle Identifier** | Will auto-generate as `com.clearancewizard.Clearance-Wizard` |
| **Interface** | **SwiftUI** ⚠️ Important! |
| **Language** | **Swift** ⚠️ Important! |
| **Storage** | None |
| **Include Tests** | Unchecked (optional) |

Click **Next**, choose a location, and click **Create**.

### 3. Set iOS Deployment Target

1. Click on the project name in the navigator (blue icon at top)
2. Under **Targets**, select "Clearance Wizard"
3. Go to **General** tab
4. Find **Minimum Deployments**
5. Set **iOS** to **17.0** or later

### 4. Add Source Files

1. In Xcode, delete the default `ContentView.swift` file (select it and press Delete, choose "Move to Trash")
2. Delete the default App file if it was named differently than `ClearanceWizardApp.swift`

Now add the files from this repository:

**Method A - Drag and Drop:**
1. Open Finder and navigate to `apps/clearance-wizard-ios/`
2. Drag these files into your Xcode project:
   - `ClearanceWizardApp.swift`
   - `ContentView.swift`
   - `ARViewContainer.swift`
3. When prompted:
   - ✅ Check "Copy items if needed"
   - ✅ Ensure "Add to targets: Clearance Wizard" is checked
   - Click **Finish**

**Method B - Add Files:**
1. Right-click on the project folder in Xcode
2. Select **Add Files to "Clearance Wizard"...**
3. Navigate to the repository's `apps/clearance-wizard-ios/` directory
4. Select all three Swift files
5. Ensure "Copy items if needed" is checked
6. Click **Add**

### 5. Update Info.plist

The project's Info.plist needs camera permission:

1. In the project navigator, click on **Info.plist**
2. Right-click in the property list area and select **Add Row**
3. Add the following key:
   - **Key**: Privacy - Camera Usage Description
   - **Type**: String
   - **Value**: Camera is required for AR measurements.

**Alternative**: You can replace the entire Info.plist:
1. Delete the existing Info.plist
2. Drag the `Info.plist` file from this repository into Xcode
3. Ensure "Copy items if needed" is checked

### 6. Add ARKit Capability (If Needed)

This should be automatic, but verify:

1. Select your project in the navigator
2. Go to **Signing & Capabilities** tab
3. Look for required device capabilities
4. Ensure **arkit** is listed

If not:
1. Click the **+** button in capabilities
2. Search for "Required Device Capabilities"
3. Add it and ensure "arkit" is included

### 7. Connect Physical Device

⚠️ **Important**: ARKit does not work in the iOS Simulator!

1. Connect your iPhone or iPad via USB
2. If prompted, trust the computer on your device
3. In Xcode, select your device from the device dropdown (next to the scheme selector at top)

### 8. Configure Signing

1. Select your project in the navigator
2. Go to **Signing & Capabilities** tab
3. Under **Signing**, check **Automatically manage signing**
4. Select your **Team** (you may need to log in with your Apple ID)
5. If you don't have a paid developer account, you can use a free personal team

### 9. Build and Run

1. Click the **Play** button (▶️) in the top-left, or press **⌘R**
2. Xcode will build the project
3. The app will install and launch on your device
4. If prompted on device, allow camera access

### 10. Test the App

1. Point your device camera at a QR code
2. The status should change from "Scanning..." to "Marker Detected"
3. A blue semi-transparent box should appear where the QR code is

## Troubleshooting

### "No such module 'RealityKit'"
- Ensure iOS Deployment Target is 17.0 or later
- RealityKit requires iOS 13.0+, but we use iOS 17 features

### "Development team not found"
- Go to Xcode → Settings → Accounts
- Add your Apple ID
- Select the team in Signing & Capabilities

### "Untrusted Developer"
- On your iOS device, go to Settings → General → VPN & Device Management
- Trust your developer certificate

### App crashes on launch
- Check if camera permission is granted
- Ensure device supports ARKit (iPhone 6S or later)
- Check Xcode console for error messages

### No QR detection
- Ensure good lighting
- Try different QR codes
- Move camera closer/farther (20-50cm is ideal)

## File Structure After Setup

Your Xcode project should look like this:

```
Clearance Wizard (Project)
├── Clearance Wizard (Target)
│   ├── ClearanceWizardApp.swift      ← Entry point
│   ├── ContentView.swift              ← Main UI
│   ├── ARViewContainer.swift          ← AR + Vision logic
│   ├── Info.plist                     ← Configuration
│   └── Assets.xcassets                ← (Default Xcode assets)
└── Products
    └── Clearance Wizard.app
```

## Next Steps

Once running successfully:
- Try different QR codes
- Move around to test anchor stability
- Check the detection info in the UI
- Consider adding AprilTag detection (see main README.md)

## Resources

- [ARKit Documentation](https://developer.apple.com/documentation/arkit)
- [Vision Framework](https://developer.apple.com/documentation/vision)
- [SwiftUI Documentation](https://developer.apple.com/documentation/swiftui)
