package lk.thiwak.megarunii.log

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.widget.TextView
import java.io.File
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.*

class LogReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        val logMessage = intent.getStringExtra("logMessage") ?: return
        val logLevel = intent.getStringExtra("logLevel") ?: "D"

        val formattedMessage = "[${getCurrentDateTime()}] [${logLevel}] $logMessage\n"

        try {
            val logFile = File(context.filesDir, "app_log.txt")
            if (!logFile.exists()) {
                logFile.createNewFile()
            }
            logFile.appendText(formattedMessage)
        } catch (e: IOException) {
            e.printStackTrace()
        }
    }

    private fun getCurrentDateTime(): String {
        val dateFormat = SimpleDateFormat("yy-MM-dd HH:mm:ss") // Define the format
        val currentDate = Date() // Get current date and time
        return dateFormat.format(currentDate) // Format the date and return
    }
}



