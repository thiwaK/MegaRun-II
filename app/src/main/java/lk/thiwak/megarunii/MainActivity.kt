package lk.thiwak.megarunii

import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.TextView
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val logTextView  = findViewById<TextView>(R.id.logView)
        LogView(logTextView )

        val textView: TextView = findViewById(R.id.text_a)

        val initialHeaders = mapOf(
            "User-Agent" to "OkHTTP",
        )
        val req:Request = Request()
        req.addHeaders(initialHeaders)

        GlobalScope.launch(Dispatchers.Main) {
            val result = withContext(Dispatchers.IO) {
                req.getData("https://duckduckgo.com", null)
            }
            textView.text = result.toString()
        }


    }
}

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