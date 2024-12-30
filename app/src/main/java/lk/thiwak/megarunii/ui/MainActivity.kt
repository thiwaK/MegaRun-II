package lk.thiwak.megarunii.ui

import android.app.ActivityManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import androidx.appcompat.app.AppCompatActivity
import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebViewClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import lk.thiwak.megarunii.*
import lk.thiwak.megarunii.log.LogReceiver
import lk.thiwak.megarunii.log.Logger
import lk.thiwak.megarunii.network.Request
import android.widget.Toast
import com.google.android.material.floatingactionbutton.FloatingActionButton

class MainActivity : AppCompatActivity() {

    private lateinit var logReceiver: LogReceiver
    private lateinit var fab: FloatingActionButton

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        fab = findViewById(R.id.fab)
        val toolbar: androidx.appcompat.widget.Toolbar = findViewById(R.id.toolbar)
        setSupportActionBar(toolbar)

        logReceiver = LogReceiver()
        registerReceiver(logReceiver, IntentFilter(Utils.LOG_INTENT_ACTION))

        if (isServiceRunning(BackgroundService::class.java, this)) {
            fab.setImageResource(R.drawable.ic_baseline_stop_circle_24) // Service is running
            Logger.debug(this, "FAB: set action to stop")
        } else {
            fab.setImageResource(R.drawable.ic_baseline_play_circle_24) // Service is not running
            Logger.debug(this, "FAB: set action to start")
        }

        fab.setOnClickListener {
            if (isServiceRunning(BackgroundService::class.java, this)) {
                // If service is running, stop the service
                stopService()
            } else {
                // If service is not running, start the service

                startService()
            }
        }

//        var browserMgr = BrowserManager()
//        browserMgr.openUrl("https://duckduckgo.com")

//        testNet()

        val intent = Intent(this, WebViewActivity::class.java)
        startActivity(intent)
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

    private fun isServiceRunning(serviceClass: Class<out Service>, context: Context): Boolean {
        val manager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        for (service in manager.getRunningServices(Integer.MAX_VALUE)) {
            if (serviceClass.name == service.service.className) {
                return true
            }
        }
        return false
    }

    private fun startService(){
        Logger.debug(this, "Action: start service")
        startService(Intent(this, BackgroundService::class.java))
        fab.setImageResource(R.drawable.ic_baseline_stop_circle_24) // Change to stop icon
        Toast.makeText(this, "Service Started", Toast.LENGTH_SHORT).show()

    }

    private fun stopService(){
        Logger.debug(this, "Action: stop service")

        val stopIntent = Intent()
        stopIntent.action = BackgroundService.STOP_SERVICE_INTENT_ACTION
        sendBroadcast(stopIntent)

        fab.setImageResource(R.drawable.ic_baseline_play_circle_24) // Change to play icon
        Toast.makeText(this, "Service Stopped", Toast.LENGTH_SHORT).show()
    }



}
