function WS(onmessage) {
	var sock = null;
	this.connect = function(wsuri) {
		if ("WebSocket" in window) {
			sock = new WebSocket(wsuri);
		}
		else if ("MozWebSocket" in window) {
			sock = new MozWebSocket(wsuri);
		}
		if (sock) {
			sock.onopen = function() {
				console.log("Connected to " + wsuri);
			}

			sock.onclose = function(e) {
				console.log("Connection closed (wasClean = " + e.wasClean + ", code = " + e.code + ", reason = '" + e.reason + "')");
				sock = null;
			}

			sock.onmessage = function(e) {
				var remote_data = JSON.parse(e.data);
				onmessage(remote_data);
			}
		}
	}

	this.disconnect = function() {
		if (sock) {
			sock.close();
			sock = null;
		}
	}
}

$(function() {
	var cpu, memory, harddisk, network;

	Highcharts.setOptions({global:{useUTC : false}});

	function spline_opt(renderTo, ytitle, unit) {
		return {
			chart: {
				renderTo: renderTo,
				type: 'spline'
			},
			title: {text: null},
			xAxis: {
				type: 'datetime',
				tickPixelInterval: 150
			},
			yAxis: {
				title: {text: ytitle+'('+unit+')'},
				labels:{
					formatter:function() {
						return this.value
					}
				}
			},
			tooltip: {
				formatter: function() {
					return '<b>'+ this.series.name+': </b>'+
					(this.y).toFixed(1)+' '+unit;
				}
			},
			plotOptions: {
				spline: {
					lineWidth: 2,
					states: {
						hover: {
							lineWidth: 3
						}
					},
					marker: {
						enabled: false
					}
				}
			},
			exporting: {enabled: false},
			series:[]
		}
	}

	function pie_opt(renderTo, name, unit) {
		return {
			chart: {
				renderTo: renderTo,
				type: 'pie'
			},
			title: {text: null},
			legend: {enabled: false},
			exporting: {enabled: false},
			tooltip: {
				formatter: function() {
					return '<b>'+ this.point.name +'</b>: '+this.point.y+' '+unit;
				}
			},
			plotOptions: {
				pie: {
					allowPointSelect: true,
					cursor: 'pointer',
					dataLabels: {
						formatter: function() {
							return '<b>'+ this.point.name +'</b>: '+ Highcharts.numberFormat(this.percentage, 2) +' %';
						}
					}
				}
			},
			series: [{
				name: name,
				data: [
					['已使用', 0],
					['未使用', 100]
				]
			}]
		}
	}

	function initHC(opt) {
		return new Highcharts.Chart(opt);
	}

	function initSpline(timestamp, item, renderTo, name, unit, flag) {
		var opt = spline_opt(renderTo,name,unit);
		
		for (var i in item) {
			opt.series.push({
				name:flag(i),
				data:(function(timestamp, y) {
					var data = [];
					for (var i = -19; i <= 0; i++) {
						data.push({
							x: timestamp + i*1000,
							y: y
						});
					}
					return data;
				})(timestamp, item[i])
			});
		}
		return initHC(opt);
	}

	memory 		= initHC(pie_opt("Memory", "内存", 'M'));
	harddisk	= initHC(pie_opt("Harddisk", "硬盘", 'G'));

	var onmessage = function(remote_data) {
		if (cpu) {
			for (var i in remote_data.cpu) {
				cpu.series[i].addPoint([remote_data.timestamp, remote_data.cpu[i]], true, true);
			}
		}
		else {
			cpu = initSpline(remote_data.timestamp, remote_data.cpu, "CPU","占用率",'%', function(i) {
				return (parseInt(i)+1)+"# CPU";
			});
		}

		if (memory.series[0].yData[0] != remote_data.memory[0] || memory.series[0].yData[1] != remote_data.memory[1]) {
			memory.series[0].setData([
				['已使用', remote_data.memory[0]],
				['未使用', remote_data.memory[1]]
			]);
		}

		if (harddisk.series[0].yData[0] != remote_data.harddisk[0] || memory.series[0].yData[1] != remote_data.harddisk[1]) {
			harddisk.series[0].setData([
				['已使用', remote_data.harddisk[0]],
				['未使用', remote_data.harddisk[1]]
			]);
		}

		if (network) {
			for (var i in remote_data.network) {
				network.series[i].addPoint([remote_data.timestamp, remote_data.network[i]], true, true);
			}
		}
		else {
			network = initSpline(remote_data.timestamp, remote_data.network, "Network","流量","byte", function(i) {
				var arr = ['发送', '接收'];
				return arr[i];
			});
		}
	}

	var ws = new WS(onmessage);
	var wsuri = "ws://" + window.location.hostname + ":9000";
	ws.connect(wsuri);

	$("#connect").click(function() {
		ws.disconnect();
		ws.connect(wsuri);
	});
	$("#disconnect").click(function() {
		ws.disconnect();
	})
});
