package lk.thiwak.megarunii.log

import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.drawable.Drawable
import android.text.*
import android.text.style.ReplacementSpan
import android.util.Log

class CustomBackgroundSpan(private val drawable: Drawable) : ReplacementSpan() {

    override fun getSize(
        paint: Paint,
        text: CharSequence,
        start: Int,
        end: Int,
        fm: Paint.FontMetricsInt?
    ): Int {
        // Calculate the width of the text
        return paint.measureText(text, start, end).toInt()
    }

    override fun draw(
        canvas: Canvas,
        text: CharSequence,
        start: Int,
        end: Int,
        x: Float,
        top: Int,
        y: Int,
        bottom: Int,
        paint: Paint
    ) {
        val parentWidth = canvas.width.toFloat()

        // Draw the background drawable
        drawable.setBounds(0, top, parentWidth.toInt(), bottom)
        drawable.draw(canvas)

        // Parse and format the log entry
        val formattedText = htmlFormatter(text.substring(start, end))

        // Use StaticLayout to render formatted text
        val staticLayout = StaticLayout.Builder
            .obtain(formattedText, 0, formattedText.length, TextPaint(paint), parentWidth.toInt())
            .setAlignment(Layout.Alignment.ALIGN_NORMAL)
            .setLineSpacing(0f, 1f)
            .build()

        canvas.save()
        canvas.translate(x, top.toFloat()) // Position text within the drawable
        staticLayout.draw(canvas)
        canvas.restore()
    }




    private fun parseLogEntry(logEntry: String): Triple<String, String, String> {
        val regex = """\[(.*?)\] \[(.*?)\] (.*)""".toRegex()
        val matchResult = regex.matchEntire(logEntry)

        return matchResult?.let {
            val (datetime, level, message) = it.destructured
            Log.i("MM", "$datetime, $level, $message")
            Triple(datetime, level, message)
        } ?:

        return Triple("", "", "")
    }

    private fun htmlFormatter(logEntry: String): Spanned {

        val (datetime, logLevel, message) = parseLogEntry(logEntry)

        var msgTextColor = "#CCCCCC" // Full brightness for the message text
        var dateTextColor = "#808080" // Darker green for datetime

        if (logLevel == "I") {
            msgTextColor = "#2481d1" // Bright light blue
            dateTextColor = "#4682B4" // Steel blue
        } else if (logLevel == "E") {
            msgTextColor = "#FF4444" // Bright red
            dateTextColor = "#8B0000" // Dark red
        } else if (logLevel == "W") {
            msgTextColor = "#FFFF00" // Bright yellow
            dateTextColor = "#B8860B" // Dark goldenrod
        }

        return Html.fromHtml(
            "<p style='font-family:monospace;'>" +
                    "<span style=\"color:$dateTextColor;\">  $datetime  </span> " +
                    "<span style=\"color:$msgTextColor style='font-size:8px;\">$message</span>" +
                    "</p>",
            Html.FROM_HTML_MODE_COMPACT
        )






    }

}
