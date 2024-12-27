package lk.thiwak.megarunii.ui

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.GestureDetector
import android.view.Menu
import android.view.MenuItem
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

class MainActivity : AppCompatActivity() {

    private lateinit var logReceiver: LogReceiver
    private lateinit var gestureDetector: GestureDetector

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // create toolbar
        val toolbar: androidx.appcompat.widget.Toolbar = findViewById(R.id.toolbar)
        setSupportActionBar(toolbar)

        // register log receiver
        logReceiver = LogReceiver()
        registerReceiver(logReceiver, IntentFilter(Utils.LOG_INTENT_ACTION))


        Logger.debug(this, "This is a debug message")
        Logger.info(this, "This is a info message")
        Logger.error(this, "This is a error message")
        Logger.warning(this, "This is a warning message")
//        registerGesture(this)
    }

    override fun onCreateOptionsMenu(menu: Menu?): Boolean {
        menuInflater.inflate(R.menu.toolbar_menu, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        when (item.itemId) {
            R.id.action_log -> {
                val intent = Intent(this, LogActivity::class.java)
                startActivity(intent)
                return true
            }
        }
        return super.onOptionsItemSelected(item)
    }

    private fun registerGesture(context: Context){
        gestureDetector = GestureDetector(this, object : GestureDetector.SimpleOnGestureListener() {
            override fun onFling(
                e1: MotionEvent?, e2: MotionEvent,
                velocityX: Float, velocityY: Float
            ): Boolean {
                if (e1 != null) {
                    if (e1.x < e2.x) {
                        openLogView(context)
                    }
                }
                return super.onFling(e1, e2, velocityX, velocityY)
            }
        })
    }

    private fun openLogView(context: Context) {
        val intent = Intent(this, LogActivity::class.java)
        startActivity(intent)
    }

    private fun testNet() {
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

