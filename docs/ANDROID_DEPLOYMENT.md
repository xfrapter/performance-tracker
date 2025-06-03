# Android Deployment Guide - Performance Tracker Mobile App

## Overview
This guide covers deploying the Performance Tracker mobile app to Android devices using Buildozer.

## Prerequisites

### 1. System Requirements
- Python 3.8+ with virtual environment
- Java Development Kit (JDK) 8 or 11
- Android SDK and NDK
- Git
- Build tools (gcc, make, etc.)

### 2. Install Java JDK
```bash
# Download and install OpenJDK 11
# Set JAVA_HOME environment variable
```

### 3. Install Android Requirements
Buildozer will automatically download Android SDK and NDK, but you can pre-install:
- Android SDK (API level 33)
- Android NDK (version 25b)
- Android Build Tools

## Deployment Steps

### 1. Prepare Environment
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install buildozer if not already installed
pip install buildozer
```

### 2. Initialize Buildozer (Already Done)
The `buildozer.spec` file is already configured with:
- App name: Performance Tracker
- Package: org.performance.performancetracker
- Required permissions for file storage
- Android API 33 with minimum API 21
- ARM64 architecture support

### 3. Build Debug APK
```bash
# First build (will take 15-30 minutes)
buildozer android debug

# Subsequent builds (faster)
buildozer android debug --profile
```

### 4. Build Release APK (For Distribution)
```bash
# Create keystore first (one-time setup)
keytool -genkey -v -keystore my-release-key.keystore -alias alias_name -keyalg RSA -keysize 2048 -validity 10000

# Build release APK
buildozer android release
```

## App Configuration Details

### Buildozer Spec Highlights
- **Target API**: Android 33 (Android 13)
- **Minimum API**: Android 21 (Android 5.0)
- **Architecture**: ARM64-v8a (64-bit)
- **Permissions**: External storage read/write for database
- **Orientation**: Portrait mode
- **Dependencies**: KivyMD, Numpy, Pandas, Matplotlib

### Database Handling
- SQLite database stored in app's internal storage
- Automatic initialization on first run
- Performance data persists across app restarts

## Installation and Testing

### Install on Device
```bash
# Install debug APK
adb install bin/performancetracker-0.1-debug.apk

# Or transfer APK file to device and install manually
```

### Testing Checklist
- [ ] App launches without crashes
- [ ] Database initializes properly
- [ ] Task creation works
- [ ] Performance recording functions
- [ ] Delay tracking operational
- [ ] History viewing displays data
- [ ] Navigation between screens smooth
- [ ] Data persistence across app restarts

## Troubleshooting

### Common Build Issues
1. **Java/JDK Issues**: Ensure JAVA_HOME is set correctly
2. **NDK Download Fails**: Check internet connection, try building with `--verbose`
3. **Permission Errors**: Run command prompt as administrator (Windows)
4. **Build Cache Issues**: Delete `.buildozer` folder and rebuild

### Runtime Issues
1. **Database Errors**: Check storage permissions
2. **UI Not Responsive**: Test on different screen sizes
3. **Performance Issues**: Monitor memory usage with larger datasets

## Performance Optimization

### APK Size
- Current dependencies may create larger APK (~50-100MB)
- Consider removing unused dependencies for production

### Runtime Performance
- SQLite operations are optimized for mobile
- UI components use KivyMD best practices
- Minimal memory footprint design

## Security Considerations

### Data Protection
- All data stored locally on device
- No network communication (offline app)
- SQLite database not encrypted (consider for sensitive data)

### Permissions
- Only requests necessary storage permissions
- No internet, camera, or location permissions

## Deployment Workflow

### Development Cycle
1. Test changes on PC with `python main.py`
2. Build debug APK: `buildozer android debug`
3. Install and test on Android device
4. Iterate and refine
5. Build release APK for distribution

### Version Management
- Update version in `buildozer.spec` for each release
- Tag releases in version control
- Maintain changelog for user updates

## Distribution Options

### Internal Distribution
- Share APK file directly
- Use internal app distribution platforms
- Email or file sharing services

### Google Play Store (Future)
- Requires release APK signing
- Play Console developer account
- App store optimization (ASO)
- Privacy policy and terms of service

## Next Steps

1. Test current debug build on Android device
2. Gather user feedback from factory workers
3. Implement requested features
4. Optimize performance based on real usage
5. Prepare for wider distribution

## File Structure for Deployment
```
PreformanceChecker/
├── main.py                 # Main app file
├── task_details.py         # Task detail screen
├── init_db.py             # Database initialization
├── buildozer.spec         # Build configuration
├── requirements.txt       # Python dependencies
├── data/                  # Database storage
├── bin/                   # Built APK files (generated)
└── .buildozer/           # Build cache (generated)
```

## Support and Maintenance

### Log Collection
- Android logs: `adb logcat`
- App-specific logs: Filter by package name
- Debug builds include verbose logging

### Updates and Patches
- Database migration scripts for schema changes
- Backward compatibility considerations
- User data preservation during updates

---

*Last Updated: December 2024*
*Version: 0.1 - Initial deployment guide* 