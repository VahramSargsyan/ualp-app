plugins {
    id("com.android.application")
}

android {
    namespace = "am.ualp.privatepilot"
    compileSdk = 35

    defaultConfig {
        applicationId = "am.ualp.privatepilot"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "0.4.3-test1"
    }

    buildTypes {
        getByName("release") {
            isMinifyEnabled = false
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
