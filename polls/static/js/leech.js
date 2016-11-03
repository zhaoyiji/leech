/**
 * Created by zhaoyiji on 2016/8/22.
 */

var baseline_x = 20;//横轴留出左右各10px的空间
var baseline_y = 420;//纵轴留出上下各10px的空间
var ENLARGE = 3;//放大倍数

function DrawMA(base, low, ma, color, cxt) {
    cxt.beginPath();
    cxt.strokeStyle = color;
    for (var i in ma) {
        // alert(low);
        // cxt.moveTo(baseline_x + ENLARGE*i, baseline_y - (ma[i]-low) * base);
        if (ma[i] == 0)
        {
            continue;
        }

        if (i == 0)
        {
            cxt.moveTo(baseline_x + ENLARGE*i, baseline_y - (ma[i]-low) * base);
        }
        else
        {
            cxt.lineTo(baseline_x + ENLARGE*i, baseline_y - (ma[i]-low) * base);
        }
    }
    cxt.stroke();
}

function DrawPen(base, low, pen, color, cxt) {
    cxt.beginPath();
    cxt.strokeStyle = color;
    for (var i in pen) {
        //alert(pen[i])
        if (i == 0)
        {
            cxt.moveTo(baseline_x + ENLARGE*pen[i][0], baseline_y - (pen[i][1]-low) * base);
        }
        else
        {
            cxt.lineTo(baseline_x + ENLARGE*pen[i][0], baseline_y - (pen[i][1]-low) * base);
        }
    }
    cxt.stroke();
}

function DrawLine(base, x, y1, y2, cxt, type, part, debug) {
    cxt.beginPath();
    cxt.moveTo(baseline_x + x, baseline_y - y1 * base);
    cxt.lineTo(baseline_x + x, baseline_y - y2 * base);
    if (debug && (type == "include"))
    {
        cxt.strokeStyle = "blue"
        cxt.stroke();
    }
    else
    {
        if (part == "top")
        {
            cxt.strokeStyle = "red"
        }
        else if (part == "bottom")
        {
            cxt.strokeStyle = "green"
        }
        else
        {
            cxt.strokeStyle = "black"
        }
        cxt.stroke();
    }
}
