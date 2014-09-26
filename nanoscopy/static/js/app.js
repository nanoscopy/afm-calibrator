var ws = null;
var plot = null;
var newWs = true;

var xmin = options.xmin;
var xmax = options.xmax;
var ymin = options.ymin;
var ymax = options.ymax;
var simul = options.simul;
var fft = options.fft;

var fmax = maxFreq;

$('#Ymin').val(ymin);
$('#Ymax').val(ymax);
var mode = null;

options.fft = $('#fft').is(':checked');
options.simul = $('#simul').is(':checked');
options.autoScale = $('#autoScaleOn').is(':checked');

function enableInputs(flag)
{
    $('#downsampling').prop('disabled', !flag); 
    $('#avgTime').prop('disabled', !flag); 
    $('#b').prop('disabled', !flag);     
    $('#L').prop('disabled', !flag); 
    $('#ro').prop('disabled', !flag);     
    $('#eta').prop('disabled', !flag); 
}

function roundMe(valore, decimali){
	return Math.round(valore*Math.pow(10,decimali))/Math.pow(10,decimali);
}

function mioLog(valore){
	return Math.log(valore)/Math.LN10;
}

function openWS(){
    if (ws === null)
    {
	ws = new WebSocket("ws://"+window.location.host+"/ws");
   
	ws.onmessage = _.throttle(function (evt) {
            msg = JSON.parse(evt.data);
            xmin = msg.xmin;
            xmax = msg.xmax;
            options.xmin = msg.xmin;
            options.xmax = msg.xmax;
            
            if (newWs)
            {
                newWs = false;
            }
            po = plot.getOptions();
            if (options.fft)
            {
                if (options.autoScale)
                {
                    ymin = msg.ymin;
                    ymax = msg.ymax;
                }
                else if (!options.fit)
                {
                    ymin = $('#Ymin').val();
                    ymax = $('#Ymax').val();
                    ymin = parseFloat(ymin);
                    ymax = parseFloat(ymax);
                }
                var corr = fmax/(xmax); //il fattore ha 'dimensioni' frequenza/indice
                                          // factor has 'size' Frequency / Index

                if(msg.draw)
                {
                    if (xmin < 1)
                    {
                       po.xaxes[0].min = 1;
                    }
                    else
                    {
                       po.xaxes[0].min = xmin;
                    }
                    po.xaxes[0].max = xmax;
                    po.xaxes[0].ticks = [[1,roundMe(corr,2)],[10,roundMe(10*corr,2)],[20,roundMe(20*corr,2)],[40,roundMe(40*corr,2)],
                    [80,roundMe(80*corr,2)],[160,roundMe(160*corr,2)],[320,roundMe(320*corr,2)],[640,roundMe(640*corr,2)],[1280,roundMe(1280*corr,2)],
                    [2560,roundMe(2560*corr,2)]];
                    po.yaxes[0].ticks = [$('#Ymin').val(),1e-4,1e-3,1e-2,1e-1,1,1e+1,1e+2,1e+3,1e+4,1e+5,1e+6,1e+7,1e+8,1e+9,1e+10,1e+11,1e+12,1e+13,1e+14,1e+15];
                    po.yaxes[0].min = ymin;
                    po.yaxes[0].max = ymax;

                    plot.setData(msg.data);
                    plot.setupGrid();
                    plot.draw();
                }
            }
            else
            {
                if (options.autoScale)
                {
                    ymin = msg.ymin;
                    ymax = msg.ymax;
                    fivePercent = (ymax - ymin) / 20;
                    ymin -= fivePercent;
                    ymax += fivePercent;
                }
                else if (!options.fit)
                {
                    ymin = $('#Ymin').val();
                    ymax = $('#Ymax').val();
                    ymin = parseFloat(ymin);
                    ymax = parseFloat(ymax);
                }
                var xstep = xmax/fmax; //(xmax/ - xmin) / 5;
                var ystep = (ymax - ymin) / 5;
                
                var tickstep = xmax/10;
                
                po.xaxes[0].ticks = [[0,0],[tickstep,roundMe(xstep/10,2)],[tickstep*2,roundMe(2*xstep/10,2)],[tickstep*3,roundMe(3*xstep/10,2)],[tickstep*4,roundMe(4*xstep/10,2)],
                [tickstep*5,roundMe(5*xstep/10,2)],[tickstep*6,roundMe(6*xstep/10,2)],[tickstep*7,roundMe(7*xstep/10,2)],[tickstep*8,roundMe(8*xstep/10,2)],
                [tickstep*9,roundMe(9*xstep/10,2)],[tickstep*10,roundMe(xstep,2)]]; //[xmin, xmin+xstep, xmin+2*xstep, xmin+3*xstep, xmin+4*xstep, xmax];
                po.yaxes[0].ticks = [ymin, ymin+ystep, ymin+2*ystep, ymin+3*ystep, ymin+4*ystep, ymax];
                po.yaxes[0].min = ymin;
                po.yaxes[0].max = ymax;
                po.xaxes[0].min = 0;
                po.xaxes[0].max = xmax;
               
                
                plot.setData(msg.data);
                plot.setupGrid();
                plot.draw();
            }
            $('#kCalc').val(msg.kc);
            $('#niR').val(msg.niR);
            $('#Qfact').val(msg.Q);
	},100);
        ws.onopen = function()
        {
            if (options.fft)
            {
                enableInputs(false);
            }
           // Web Socket is connected, send data using send()
           ws.send(JSON.stringify(options));
        };
    }
}
	
function closeWS(){
    newWs = true;
    ws.close();
    ws = null;
    enableInputs(true);
}

$('#flot').bind("plotselected",
    function (event, ranges)
    {
        if (options.fit)
        {
            options.fitmin = parseInt(ranges.xaxis.from);
            options.fitmax = parseInt(ranges.xaxis.to);
        }
        else
        {
            options.xmin = parseInt(ranges.xaxis.from)*2;
            options.xmax = parseInt(ranges.xaxis.to)*2;
            if (!options.autoScale)
            {
               $('#Ymin').val(parseFloat(ranges.yaxis.from).toPrecision(3));
               $('#Ymax').val(parseFloat(ranges.yaxis.to).toPrecision(3));
            }
        }
        if (ws)
            ws.send(JSON.stringify(options));
    }
);

$('#flot').bind("plotunselected",
    function (event, ranges)
    {
        options.xmin = xmin;
        options.xmax = xmax;
        options.ymin = ymin;
        options.ymax = ymax;
        if (ws)
            ws.send(JSON.stringify(options));
    }
);

var plot = $.plot("#flot", [d1], {
		xaxis: {transform:  function(v) {
					if ($('#fft').is(':checked')) return mioLog(v+0.001);
					else return v;
				} ,
				inverseTransform:  function(v) {
					if ($('#fft').is(':checked')) return Math.pow(10,v);
					else return v;
				} , 
				tickDecimals: 2 ,
				//scale: 0.15 ,
				tickFormatter: function (v, axis) {
					if ($('#fft').is(':checked')) return "10" + (Math.round(mioLog(v))).toPrecision(3).toString().sup();
					else return v.toPrecision(3);
				}
			},
		selection: {
                                mode: "xy"
			},
		yaxis: {transform:  function(v) {
					if ($('#fft').is(':checked')) return mioLog(v);
					else return v;
				} ,
				inverseTransform:  function(v) {
					if ($('#fft').is(':checked')) return Math.pow(10,v);
					else return v;
				} ,
				tickDecimals: 10 ,
				tickFormatter: function (v, axis) {
					if ($('#fft').is(':checked')) return "10" + (Math.round( mioLog(v))).toPrecision(3).toString().sup();
					else return v.toPrecision(3);
				}
			},
		
		points: {show: false, radius: 1},
		lines: {show: true},
		shadowSize: 0
	}
);

updateDownsampling = _.debounce(function(){
		options.downsampling = parseInt($('#downsampling').val()) || 1;
		if (ws)
			ws.send(JSON.stringify(options));
	},
	250);

$('#downsampling').val(options.downsampling);

$('#downsampling').keyup(updateDownsampling);

updateRo = _.debounce(function(){
		options.ro = parseInt($('#ro').val()) || 1;
		if (ws)
			ws.send(JSON.stringify(options));
	},
	250);

$('#ro').val(options.ro);

$('#ro').keyup(updateRo);

updateEta = _.debounce(function(){
		options.eta = parseInt($('#eta').val()) || 1;
		if (ws)
			ws.send(JSON.stringify(options));
	},
	250);

$('#eta').val(options.eta);

$('#eta').keyup(updateEta);

updateB = _.debounce(function(){
		options.b = parseInt($('#b').val()) || 1;
		if (ws)
			ws.send(JSON.stringify(options));
	},
	250);

$('#b').val(options.b);

$('#b').keyup(updateB);

updateL = _.debounce(function(){
		options.L = parseInt($('#L').val()) || 1;
		if (ws)
			ws.send(JSON.stringify(options));
	},
	250);

$('#L').val(options.L);

$('#L').keyup(updateL);

updateAvgTime = _.debounce(function(){
		options.avgT = parseFloat($('#avgTime').val()) || 1;
		if (ws)
			ws.send(JSON.stringify(options));
	},
	250);

$('#avgTime').val(options.avgT);

$('#avgTime').keyup(updateAvgTime);

$('#simul').change(function(){
		options.simul = $('#simul').is(':checked');
		if (options.simul)
		{
			xmax = xmaxS;
			fmax = maxFreqS;
			options.xmax = xmaxS;
		}
		else
		{
			xmax = xmax2;
			fmax = maxFreq;
			options.xmax = xmax2;
		}
		
		if(ws)
			ws.send(JSON.stringify(options));
	}
);


$('#fft').change(function(){
		options.fft = $('#fft').is(':checked');
                $('#fitOn').prop('disabled', !options.fft);
		
		if(ws)
                {
                    if (options.fft)
                    {
                        enableInputs(false);
                    }
                    else
                    {
                        enableInputs(true);
                    }
                    ws.send(JSON.stringify(options));
                }
	}
 );
        
$('#autoScaleOn').change(function(){
                if (options.autoScale !== $('#autoScaleOn').is(':checked'))
                {
                    options.autoScale = $('#autoScaleOn').is(':checked');
                    options.fit = $('#fitOn').is(':checked');
                    options.xmin = xmin*2;
                    options.xmax = xmax*2;
                    mode = null;
		
                    if(ws)
			ws.send(JSON.stringify(options));
                }
	}
);

$('#zoomOn').change(function(){
		if (options.autoScale !== $('#autoScaleOn').is(':checked'))
                {
                options.autoScale = !$('#zoomOn').is(':checked');
                options.fit = $('#fitOn').is(':checked');
		
		if(ws)
			ws.send(JSON.stringify(options));
                }
	}
);
        
$('#fitOn').change(function(){
                if ($('#fft').is(':checked'))
                {
		   options.autoScale = !$('#fitOn').is(':checked');
                   options.fit = $('#fitOn').is(':checked');
		
		   if(ws)
                      ws.send(JSON.stringify(options));
                }
                else if (options.autoScale)
                {
		   $('#autoScaleOn').checked(true);                    
                }
                else
                {
                   $('#zoomOn').checked(true);
                }
	}
                
);
