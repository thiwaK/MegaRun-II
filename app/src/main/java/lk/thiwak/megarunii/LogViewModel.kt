package lk.thiwak.megarunii

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle

class LogViewModel : ViewModel() {
    // Expose the LiveData from LogManager
    val logMessages = LogManager.logMessages

    // Provide a method to add logs via LogManager
    fun addLog(message: String, level: LogManager.LogLevel = LogManager.LogLevel.INFO) {
        LogManager.log(message, level)
    }

    // Method to clear logs
    fun clearLogs() {
        LogManager.clearLogs()
    }
}