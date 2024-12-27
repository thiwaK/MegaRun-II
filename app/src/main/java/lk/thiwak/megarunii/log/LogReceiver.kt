package lk.thiwak.megarunii.log

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.widget.TextView
import java.io.File
import java.io.IOException

class LogReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        val logMessage = intent.getStringExtra("logMessage") ?: return
        val logLevel = intent.getStringExtra("logLevel") ?: "D"

        val formattedMessage = "[${logLevel}] $logMessage\n"

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
}



