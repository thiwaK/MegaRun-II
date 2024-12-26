package lk.thiwak.megarunii

import android.widget.TextView

class LogView(private var logView:TextView) {

    private val logBuilder = StringBuilder()
    enum class LogLevel { DEBUG, INFO, WARN, ERROR }

    private fun log(message: String, level: LogLevel = LogLevel.INFO) {
        val formattedMessage = "[${level.name}] $message\n"
        logBuilder.append(formattedMessage)

        logView?.post {
            logView?.text = logBuilder.toString()
        }
    }

    fun info(message: String) = log(message, LogLevel.INFO)
    fun error(message: String) = log(message, LogLevel.ERROR)
    fun warning(message: String) = log(message, LogLevel.WARN)
    fun debug(message: String) = log(message, LogLevel.DEBUG)

    fun clear() {
        logBuilder.clear()
        logView?.post { logView?.text = "" }
    }
}



