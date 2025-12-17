# Changelog - Clearance Wizard iOS

All notable changes to the iOS native Clearance Wizard app will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Architecture
- Monorepo structure with apps/ and packages/
- React Native 0.73 for UI layer
- Swift ARKit native module for AR functionality
- TypeScript for type safety

### Added - M1: ARKit Bridge (Complete)
- Swift ARKit native module (`ARKitBridge.swift`)
- Objective-C bridge for React Native integration
- TypeScript wrapper with full type safety
- Session management (start/stop)
- Hit testing for surface detection
- World anchor creation and management
- Distance measurement between two points
- Photo capture from AR frame
- Tracking state monitoring
- Event system (onFrame, onAnchorUpdate, onError)
- Camera intrinsics and transform updates

### Added - M2: Measurement Tools (Partial)
- Basic point-to-point measurement
- Confidence scoring based on plane detection
- Real-time measurement display
- Measurement save/discard workflow

### Added - UI Screens (Complete)
- Home screen with pack list
- Site details entry screen (optional metadata)
- AR measurement screen with live camera
- Export screen with pack summary
- Navigation system with React Navigation

### Added - Type Definitions
- Shared TypeScript types in `@clearance-wizard/core`
- Pack schema definition
- Capture and Measurement types
- AR context types (intrinsics, transform, tracking state)

### Added - Documentation
- Comprehensive README with architecture overview
- Quick start guide (QUICKSTART_IOS.md)
- Implementation summary (IOS_NATIVE_IMPLEMENTATION.md)
- Code comments and JSDoc documentation

### TODO - M2: Measurement Tools (Remaining)
- [ ] Confidence gating logic
- [ ] Measurement repeatability validation
- [ ] Visual feedback for anchor placement
- [ ] Measurement history in UI

### TODO - M3: Pack Storage
- [ ] SQLite database implementation
- [ ] Pack CRUD operations
- [ ] Photo filesystem management
- [ ] ZIP export with images

### TODO - M4: Polish
- [ ] Error handling improvements
- [ ] Performance optimization
- [ ] Loading states and animations
- [ ] User feedback and help system
- [ ] Field testing and validation

## [0.1.0] - 2024-12-17

### Initial Release
- Foundation for iOS-native Clearance Wizard
- ARKit integration complete
- Basic measurement workflow functional
- Local-first architecture established
