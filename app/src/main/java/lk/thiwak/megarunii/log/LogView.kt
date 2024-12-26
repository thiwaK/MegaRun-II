package lk.thiwak.megarunii.log

import android.widget.TextView

class LogView(private var logView:TextView) {

    private val logBuilder = StringBuilder()
    enum class LogLevel { DEBUG, INFO, WARN, ERROR }

    private fun log(message: String, level: LogLevel) {
        val formattedMessage = "[${level.name}] $message\n"
        logBuilder.append(formattedMessage)

        logView?.post {
            logView?.text = logBuilder.toString()
        }
    }

    fun clear() {
        logBuilder.clear()
        logView?.post { logView?.text = "" }
    }
}



