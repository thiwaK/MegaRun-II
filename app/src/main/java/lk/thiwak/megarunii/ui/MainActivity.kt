package lk.thiwak.megarunii.ui

import android.content.IntentFilter
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.widget.TextView
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import lk.thiwak.megarunii.*
import lk.thiwak.megarunii.log.LogReceiver
import lk.thiwak.megarunii.log.Logger
import lk.thiwak.megarunii.network.Request

class MainActivity : AppCompatActivity() {

    private lateinit var logReceiver: LogReceiver
    private lateinit var logView: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        logView = findViewById(R.id.text_a)
        logReceiver = LogReceiver(logView)

        val filter = IntentFilter(Utils.LOG_INTENT_ACTION)
        registerReceiver(logReceiver, filter)


        Logger.debug(this, "This is a debug message")

        testNet()

        Logger.info(this, "This is a info message")

    }

    fun testNet() {
        val initialHeaders = mapOf(
            "User-Agent" to "OkHTTP",
        )
        val req: Request = Request(this)
        req.addHeaders(initialHeaders)

        GlobalScope.launch(Dispatchers.IO) {
            val result = withContext(Dispatchers.IO) {
                req.getData("https://duckduckgo.com", null)
            }
        }
    }
}

