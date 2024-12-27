package lk.thiwak.megarunii.log

import android.content.Context
import android.content.Intent
import lk.thiwak.megarunii.Utils

class Logger {

    enum class LogLevel { DEBUG, INFO, WARN, ERROR }

    companion object {

        private fun log(context: Context, message: String, level: LogLevel) {
            val intent = Intent(Utils.LOG_INTENT_ACTION)
            intent.putExtra("logMessage", message)
            if (level == LogLevel.DEBUG){ intent.putExtra("logLevel", "D")}
            if (level == LogLevel.INFO){ intent.putExtra("logLevel", "I")}
            if (level == LogLevel.WARN){ intent.putExtra("logLevel", "W")}
            if (level == LogLevel.ERROR){ intent.putExtra("logLevel", "E")}

            context.sendBroadcast(intent)
        }
        fun info(context: Context, message: String) = log(context, message, LogLevel.INFO)
        fun error(context: Context, message: String) = log(context, message, LogLevel.ERROR)
        fun warning(context: Context, message: String) = log(context, message, LogLevel.WARN)
        fun debug(context: Context, message: String) = log(context, message, LogLevel.DEBUG)
    }
}