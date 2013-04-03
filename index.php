<!DOCTYPE html>
<html>
<head>
<meta http-equip="Content-Type" content="text/html;charset=utf-8">
<title>Web Monitor</title>
<link rel = "stylesheet" type="text/css" href = "css/server.css"></style>
</head>
<body>
<div class="panel">
	<h2 class="option">CPU</h2>
	<div id="CPU" class="chart" style="height:300px;"></div>
</div>
<div class="panel" style="width:48%; float:left">
	<h2 class="option">内存</h2>
	<div id="Memory" class="chart" style="height:300px;"></div>
</div>
<div class="panel" style="width:48%; float:right">
	<h2 class="option">硬盘</h2>
	<div id="Harddisk" class="chart" style="height:300px;"></div>
</div>
<div class="panel" style="clear:both">
	<h2 class="option">网络</h2>
	<div id="Network" class="chart" style="height:300px;"></div>
</div>

<div id="control">
	<input id="connect" class="btn" type="button" value="打开连接" />
	<input id="disconnect" class="btn" type="button" value="关闭连接" />
</div>

<script type = "text/javascript" src = "js/jquery.min.js"></script>
<script type = "text/javascript" src = "js/highcharts.js"></script>
<script type = "text/javascript" src = "js/server.js"></script>
</body>
</html>

	
