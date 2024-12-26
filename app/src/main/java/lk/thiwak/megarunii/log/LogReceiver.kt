package lk.thiwak.megarunii.log

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.widget.TextView

class LogReceiver(private val logView: TextView) : BroadcastReceiver() {
    private val logBuilder = StringBuilder()

    override fun onReceive(context: Context, intent: Intent) {
        val logMessage = intent.getStringExtra("logMessage") ?: return
        val logLevel = intent.getStringExtra("logLevel") ?: "D"

        val formattedMessage = "[${logLevel}] $logMessage\n"
        logBuilder.append(formattedMessage)

        logView.post {
            logView.text = logBuilder.toString()
        }
    }
}


