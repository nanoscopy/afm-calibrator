var ws = null;
var plot = null;

var xmax = options.xmax;

var fmax = maxFreq;

$('#Ymin').val('-3.3e+4');
$('#Ymax').val('3.3e+4');

function roundMe(valore, decimali){
	return Math.round(valore*Math.pow(10,decimali))/Math.pow(10,decimali);
}

function mioLog(valore){
	return Math.log(valore)/Math.LN10;
}

function openWS(){
	ws = new WebSocket("ws://"+window.location.host+"/ws");
	ws.onmessage = _.throttle(function (evt) {
		msg = JSON.parse(evt.data);
		if (options.fft)
		{
			var corr = fmax/(xmax/4); //il fattore ha 'dimensioni' frequenza/indice
			//console.log(xmax);
			//console.log(fmax);
			
			if(msg.draw){
				plot.getOptions().xaxes[0].min = 5;
				plot.getOptions().xaxes[0].ticks = [[1,roundMe(corr,2)],[10,roundMe(10*corr,2)],[20,roundMe(20*corr,2)],[40,roundMe(40*corr,2)],
				[80,roundMe(80*corr,2)],[160,roundMe(160*corr,2)],[320,roundMe(320*corr,2)],[640,roundMe(640*corr,2)],[1280,roundMe(1280*corr,2)],
				[2560,roundMe(2560*corr,2)]];
				plot.getOptions().yaxes[0].ticks = [$('#Ymin').val(),1e+6,1e+7,1e+8,1e+9,1e+10,1e+11,1e+12,1e+13,1e+14,1e+15];
				plot.getOptions().yaxes[0].min = $('#Ymin').val();
				plot.getOptions().yaxes[0].max = $('#Ymax').val();
				plot.setData(msg.data);
				plot.setupGrid();
				plot.draw();
			}
		}
		else
		{
			var max = xmax;
			plot.getOptions().xaxes[0].ticks = [0, max/10, 2*max/10, 2*max/10, 3*max/10, 4*max/10, 5*max/10, 6*max/10, 7*max/10, 8*max/10, 9*max/10];
			plot.getOptions().yaxes[0].ticks = [-30000,-20000,-10000,0,10000,20000,30000];
			plot.getOptions().yaxes[0].min = $('#Ymin').val();
			plot.getOptions().yaxes[0].max = $('#Ymax').val();
			plot.setData(msg.data);
			plot.setupGrid();
			plot.draw();
		}
		$('#kCalc').val(msg.kc);
		$('#niR').val(msg.niR);
		$('#Qfact').val(msg.Q);
	},100);
}
	
function closeWS(){
	ws.close();
}

$('#flot').bind("plotselected", function (event, ranges) {	
		options.xmin = parseInt(ranges.xaxis.from);
		options.xmax = parseInt(ranges.xaxis.to);
		if (ws)
			ws.send(JSON.stringify(options));
	}
);

$('#flot').bind("plotunselected", function (event, ranges) {	
		options.xmin = 0;
		options.xmax = xmax;
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
					if ($('#fft').is(':checked')) return "10" + (Math.round(mioLog(v))).toString().sup();
					else return v;
				}
			},
		selection: {
				mode: "x"
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
					if ($('#fft').is(':checked')) return "10" + (Math.round( mioLog(v))).toString().sup();
					else return v;
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
		if ($('#fft').is(':checked'))
		{
			$('#Ymin').val('1e+4');
			$('#Ymax').val('1e+16');
		}
		else
		{
			$('#Ymin').val('-3.3e+4');
			$('#Ymax').val('3.3e+4');
		}
		if(ws)
			ws.send(JSON.stringify(options));
	}
);
