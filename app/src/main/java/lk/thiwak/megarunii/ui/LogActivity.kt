package lk.thiwak.megarunii.ui

import android.annotation.SuppressLint
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.graphics.Color
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.text.SpannableString
import android.text.Spanned
import android.text.style.ForegroundColorSpan
import android.view.GestureDetector
import android.widget.TextView
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import lk.thiwak.megarunii.*
import lk.thiwak.megarunii.log.LogReceiver
import lk.thiwak.megarunii.log.Logger
import lk.thiwak.megarunii.network.Request
import android.view.MotionEvent
import android.widget.ScrollView
import java.io.File
import java.io.IOException
import java.io.RandomAccessFile

class LogActivity : AppCompatActivity() {


    private var currentPosition: Long = 0 // Tracks the current read position
    private val chunkSize = 1024 // Number of characters to read in each chunk
    private val logFileName = "app_log.txt"
    private lateinit var logScrollView: ScrollView
    private lateinit var logView: TextView


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_log)

        logScrollView = findViewById(R.id.logScrollView)
        logView = findViewById(R.id.logView)

        logScrollView.viewTreeObserver.addOnScrollChangedListener {
            val view = logScrollView.getChildAt(logScrollView.childCount - 1)
            val diff = (view.bottom - (logScrollView.height + logScrollView.scrollY))

            if (diff == 0) {
                appendLogChunk()
            }
        }

        appendLogChunk()

    }

    private fun appendLogChunk() {
        try {
            val logFile = File(filesDir, logFileName)
            if (logFile.exists()) {
                RandomAccessFile(logFile, "r").use { reader ->
                    reader.seek(currentPosition)
                    val buffer = ByteArray(chunkSize)
                    val charsRead = reader.read(buffer)
                    if (charsRead > 0) {
                        val newContent = String(buffer, 0, charsRead)
                        currentPosition += charsRead

                        // Process each log entry and color based on level
                        val logEntries = newContent.split("\n") // Split by lines
                        logEntries.forEach { logEntry ->
                            val (logLevel, message) = parseLogEntry(logEntry) // Parse the log entry into level and message
                            val coloredMessage = applyLogColor(logLevel, message)

                            // Append the styled message to TextView
                            logView.append(coloredMessage)
                        }
                    }
                }
            } else {
                logView.text = "No logs available."
            }
        } catch (e: IOException) {
            e.printStackTrace()
            logView.text = "Error loading logs."
        }
    }

    private fun parseLogEntry(logEntry: String): Pair<String, String> {
        val parts = logEntry.split(" ", limit = 2)
        return if (parts.size == 2) {
            parts[0] to parts[1]
        } else {
            "INFO" to logEntry
        }
    }

    private fun applyLogColor(logLevel: String, message: String): SpannableString {
        val spannableMessage = SpannableString(message)

        when (logLevel) {
            "INFO" -> spannableMessage.setSpan(ForegroundColorSpan(Color.BLUE), 0, message.length, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
            "ERROR" -> spannableMessage.setSpan(ForegroundColorSpan(Color.RED), 0, message.length, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
            "WARN" -> spannableMessage.setSpan(ForegroundColorSpan(Color.YELLOW), 0, message.length, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
            "DEBUG" -> spannableMessage.setSpan(ForegroundColorSpan(Color.GREEN), 0, message.length, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
            else -> spannableMessage.setSpan(ForegroundColorSpan(Color.GRAY), 0, message.length, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
        }

        return spannableMessage
    }
}