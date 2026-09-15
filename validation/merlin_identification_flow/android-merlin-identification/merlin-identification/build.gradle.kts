plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.anura.merlin.identification"
    compileSdk = 35
    defaultConfig { minSdk = 26 }
}

kotlin { jvmToolchain(17) }

dependencies {
    implementation("com.microsoft.onnxruntime:onnxruntime-android:1.20.0")
}
