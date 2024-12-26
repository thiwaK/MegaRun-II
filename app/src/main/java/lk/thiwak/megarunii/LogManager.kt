package lk.thiwak.megarunii

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData

object LogManager {

    private val _logMessages = MutableLiveData<StringBuilder>()
    val logMessages: LiveData<StringBuilder> get() = _logMessages
    private val logBuilder = StringBuilder()
    enum class LogLevel { DEBUG, INFO, WARN, ERROR }

    fun log(message: String, level: LogLevel = LogLevel.INFO) {
        val formattedMessage = "[${level.name}] $message\n"
        logBuilder.append(formattedMessage)
        _logMessages.postValue(logBuilder)
    }

    fun clearLogs() {
        logBuilder.clear()
        _logMessages.postValue(logBuilder)
    }
}
