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
import android.webkit.WebView
import android.widget.ScrollView
import androidx.core.content.ContextCompat
import java.io.File
import java.io.IOException
import java.io.RandomAccessFile
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.drawable.Drawable
import android.os.Build
import android.text.Html
import android.text.style.ReplacementSpan
import android.util.Log
import androidx.annotation.RequiresApi
import lk.thiwak.megarunii.log.CustomBackgroundSpan

class LogActivity : AppCompatActivity() {


    private var currentPosition: Long = 0
    private val chunkSize = 1024*10
    private val logFileName = "app_log.txt"
    private lateinit var logScrollView: ScrollView
    private lateinit var logView: TextView
    private lateinit var logBgDrawable:Drawable
    val TAG:String = "LogActivity"


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

        logScrollView.post {
            logScrollView.scrollTo(0, logScrollView.getChildAt(0).height)
        }

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

                        val logEntries = newContent.split("\n") // Split by lines
                        var count = 0;

                        logEntries.forEach { logEntry ->
                            // val formattedLogEntry = htmlFormatter(logEntry)

                            if (logEntry.trim().isEmpty()){
                                return@forEach
                            }

                            val (date, logLevel, message) = parseLogEntry(logEntry)

                            if (date.isEmpty() || logLevel.isEmpty() || message.isEmpty()){
                                return@forEach
                            }

                            logBgDrawable = if (count%2 == 0){
                                ContextCompat.getDrawable(this, R.drawable.log_box_background_a)!! } else {
                                ContextCompat.getDrawable(this, R.drawable.log_box_background_b)!! }



                            // val coloredMessage = applyLogColor(logLevel, message, count%2)
                            var spannableMessage = SpannableString(logEntry)
                            spannableMessage.setSpan(
                                CustomBackgroundSpan(logBgDrawable),
                                0,
                                logEntry.length,
                                Spanned.SPAN_EXCLUSIVE_EXCLUSIVE
                            )
                            logView.append(spannableMessage)
                            count += 1


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


    private fun parseLogEntry(logEntry: String): Triple<String, String, String> {
        val regex = """\[(.*?)\] \[(.*?)\] (.*)""".toRegex()
        val matchResult = regex.matchEntire(logEntry)

        return matchResult?.let {
            val (datetime, level, message) = it.destructured
            Triple(datetime, level, message)
        } ?:

        return Triple("", "", "")


//        val parts = logEntry.split(" ", limit = 3)
//        Log.i(TAG, "$parts[0] $parts[1] $parts[2]\n")
//        return if (parts.size == 3) {
//            parts[1] to  "$parts[0] $parts[1] $parts[2]\n"
//
//        } else {
//            "[D]" to logEntry
//        }
    }

}


