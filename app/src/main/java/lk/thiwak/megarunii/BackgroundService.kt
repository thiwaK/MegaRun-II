package lk.thiwak.megarunii

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.util.Log
import androidx.core.app.NotificationCompat
import lk.thiwak.megarunii.log.LogReceiver
import lk.thiwak.megarunii.log.Logger
import kotlin.properties.Delegates

class BackgroundService : Service() {

    private lateinit var logReceiver: LogReceiver
    private lateinit var stopReceiver: StopReceiver
    private var startTime by Delegates.notNull<Long>()
    private lateinit var notificationManager: NotificationManager
    private lateinit var notificationBuilder: NotificationCompat.Builder
    private lateinit var handler: Handler
    private lateinit var runnable:Runnable
    private lateinit var backgroundThread: Worker
    private var shouldRun by Delegates.notNull<Boolean>()

    companion object {
        const val CHANNEL_ID = "MegaRunIIBackgroundServiceChannel"
        const val STOP_SERVICE_INTENT_ACTION = "lk.thiwak.megarunii.STOP_SERVICE"

    }

    override fun onCreate() {
        super.onCreate()
        logReceiver = LogReceiver()
        registerReceiver(logReceiver, IntentFilter(Utils.LOG_INTENT_ACTION))
        stopReceiver = StopReceiver()
        registerReceiver(stopReceiver, IntentFilter(STOP_SERVICE_INTENT_ACTION))

        startTime = System.currentTimeMillis()
        shouldRun = true

        notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        notificationBuilder = getNotificationBuilder()

        // Start service in foreground
        startForeground(1, notificationBuilder.build())

        // Set up the handler to update the notification every second
        runnable = object : Runnable {
            override fun run() {
                if (shouldRun) {
                    updateNotification()
                    handler.postDelayed(this, 1000) // Update every second
                }
            }
        }
        handler = Handler(Looper.getMainLooper())
        handler.post(runnable)


        Logger.info(this, "Service created")
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Logger.info(this, "Service started")
        performBackgroundTask()
        return START_STICKY // Keep the service running unless explicitly stopped
    }

    override fun onDestroy() {
        super.onDestroy()
        try {
            unregisterReceiver(logReceiver)
            unregisterReceiver(stopReceiver)
        } catch (e: IllegalArgumentException) {
            e.printStackTrace()
        }
        Logger.info(this, "Service destroyed")
    }

    override fun onBind(intent: Intent?): IBinder? {
        // Binding not supported
        return null
    }

    private fun getNotificationBuilder(): NotificationCompat.Builder {
        // Create notification channel for Android 8.0 and above
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val name = "MegaRun-II Background Service"
            val descriptionText = "Notification for the MegaRun-II background service"
            val importance = NotificationManager.IMPORTANCE_DEFAULT
            val channel = NotificationChannel(CHANNEL_ID, name, importance).apply {
                description = descriptionText
            }
            val notificationManager: NotificationManager =
                getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }

        // Create the notification for the service
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Background Service Running")
            .setContentText("Self playing is active.")
            .setOnlyAlertOnce(true)
            .setProgress(40, 20, false)
            .setOngoing(true)
            .setSmallIcon(R.drawable.ic_baseline_play_circle_24) // Replace with your icon
    }

    private fun getElapsedTime(): String {
        val elapsedMillis = System.currentTimeMillis() - startTime
        val seconds = (elapsedMillis / 1000) % 60
        val minutes = (elapsedMillis / (1000 * 60)) % 60
        val hours = (elapsedMillis / (1000 * 60 * 60)) % 24

        // Format time as HH:mm:ss
        return String.format("%02d:%02d:%02d", hours, minutes, seconds)
    }

    private fun updateNotification() {
        val elapsedTime = getElapsedTime()
        notificationBuilder.setContentText("Elapsed Time: $elapsedTime")
        notificationManager.notify(1, notificationBuilder.build())
    }

    private fun performBackgroundTask() {
        // Start a background thread to simulate work
        backgroundThread = Worker(this)
        backgroundThread?.start()
    }

    // BroadcastReceiver to stop the service
    private inner class StopReceiver : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            Log.i("BackgroundService", "Stop action received, stopping service...")
            backgroundThread.stopNow()

            while (backgroundThread?.isAlive == true){
                Thread.sleep(1000)
            }
            Log.i("BackgroundService", "Thread stopped.")

            shouldRun = false
            handler.removeCallbacks(runnable)
            stopSelf()
        }
    }
}
