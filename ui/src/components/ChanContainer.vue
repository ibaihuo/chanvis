<template>
<div class="ChanContainer" :id="containerId" />
</template>

<script>
 
import { widget } from '../../public/charting_library';

const axios = require('axios');

function getLanguageFromURL() {
  const regex = new RegExp('[\\?&]lang=([^&#]*)');
  const results = regex.exec(window.location.search);
  return results === null ? null : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

// 忽略所有警告信息

export default {
  name: 'ChanContainer',
  props: {
    symbol: {
      default: '000001.XSHG',
      // default: 'BTC',
      type: String,
    },
    interval: {
      // default: '1D',
      default: '1D',
      type: String,
    },
    containerId: {
      default: 'tv_chart_container',
      type: String,
    },
    datafeedUrl: {
    // default: 'https://demo_feed.tradingview.com',
    default: 'http://127.0.0.1:8421/api',
      type: String,
    },
    libraryPath: {
      default: '/charting_library/',
      type: String,
    },
    chartsStorageUrl: {
      // 后面不要带符号【/】
      default: 'http://127.0.0.1:8000',
      type: String,
    },
    chartsStorageApiVersion: {
      default: '1.1',
      type: String,
    },
    clientId: {
      default: 'quantchan.com',
      type: String,
    },
    userId: {
      default: 'baihuo',
      type: String,
    },
    fullscreen: {
      default: false,
      type: Boolean,
    },
    autosize: {
      default: true,
      type: Boolean,
    },
    studiesOverrides: {
      type: Object,
    }
  },
  tvWidget: null,
  mounted() {
    const widgetOptions = {
      symbol: this.symbol,
      // BEWARE: no trailing slash is expected in feed URL
      // 每一秒刷新一次K线接口
      datafeed: new window.Datafeeds.UDFCompatibleDatafeed(this.datafeedUrl, 5000),
      // datafeed: new window.Datafeeds.UDFCompatibleDatafeed(this.datafeedUrl),
      interval: this.interval,
      container_id: this.containerId,
      library_path: this.libraryPath,

      locale: getLanguageFromURL() || 'zh',
      // disabled_features: ['use_localstorage_for_settings'],
      enabled_features: ['study_templates'],
      charts_storage_url: this.chartsStorageUrl,
      charts_storage_api_version: this.chartsStorageApiVersion,
      client_id: this.clientId,
      user_id: this.userId,
      fullscreen: this.fullscreen,
      autosize: this.autosize,
      studies_overrides: this.studiesOverrides,
      debug: true,
      supported_resolution:  ["1", "5", "30", "240", "D"],
      customFormatters: {
        timeFormatter: {
            format: function (date) {
              let hour = date.getHours();
              let minute = date.getMinutes();
              hour = hour < 10 ? ('0' + hour) : hour;
              minute = minute < 10 ? ('0' + minute) : minute;

              return hour + ':' + minute;
            }
        },
        dateFormatter: {
          format: function (date) {
            let year = date.getFullYear();
            let month = date.getMonth() + 1;
            let day = date.getDate();

            month = month < 10 ? ('0' + month) : month;
            day = day < 10 ? ('0' + day) : day;

            return year + '-' + month + '-' + day + ' ';
          }
        }
      },
      // 初始的获取数据窗口大小，获取最近的50个月的数据
      timeframe: '250M',

      favorites: {
        intervals: ["1", "5", "30", "240", "D", "W"],
        chartTypes: ["Bar", "Line"]
      },

      overrides: {
				"paneProperties.background": "#181B2A",
				"paneProperties.vertGridProperties.color": "#454545",
				"paneProperties.horzGridProperties.color": "#454545",
				"symbolWatermarkProperties.transparency": 90,
				"scalesProperties.textColor": "#AAA",
				'scalesProperties.fontSize': 13,
				'paneProperties.legendProperties.showLegend': false,
				"symbolWatermarkProperties.color": "rgba(0, 0, 0, 0.00)",
				"volumePaneSize": "small",
				"scalesProperties.showRightScale": false,
      },

      // 自定义指标的配置
      custom_indicators_getter: function(PineJS) {
         return Promise.resolve([

        
        // 新定义NMA一个指标
        {
          name: 'NMA',
          metainfo: {
              '_metainfoVersion': 40,
              'id': 'NMA@tv-basicstudies-1',
              'scriptIdPart': '',
              'name': 'NMA',
              //当调用createStudy方法时，它也被用作“name”参数
              'description': 'NMA',
              // 该描述将显示在图表上
              'shortDescription': 'NMA',
              'is_hidden_study': true,
              // 指标曲线是否在主数据列窗口中显示
              'is_price_study': true,
              'isCustomIndicator': true,
              'plots': [{
                  'id': 'plot_0',
                  'type': 'line'
              },{
                  'id': 'plot_1',
                  'type': 'line'
              },
              ],
              'defaults': {
                  'styles': {
                      'plot_0': {
                          'linestyle': 0,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 2, // 绘制类型为线形图： 2
                          'trackPrice': false,
                          'transparency': 10,
                          'color': '#FFFF00'
                      },
                      'plot_1': {
                          'linestyle': 0,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 2, // 绘制类型为线形图： 2
                          'trackPrice': false,
                          'transparency': 10,
                          'color': '#FF0000'
                      },
                  },
                  'precision': 2, // 精度 eg：608.4
                  'inputs': {}
              },
              'styles': {
                  'plot_0': {
                      'title': 'nma',
                      'histogrambase': 0,
                  },
              },
              'inputs': [],
          },
          constructor: function () {
              this.init = function (context, inputCallback) {
                  var fakeDataRSI = [];
                  let sym = tvWidget.activeChart().symbol()
                  let freq = tvWidget.activeChart().resolution()

                  // 获取指标数据
                  axios
                    .get('http://127.0.0.1:8421/api/get_ocean_ind?resolution='+freq+'&symbol='+sym+'&ind=nma')
                    .then((res) => {
                        if(res.data.status == 'ok'){
                          fakeDataRSI = res.data.data
                          this.fakeData = fakeDataRSI
                        }
                      }
                    )
                  
                  // this.fakeData = fakeDataRSI;
                  // console.log(';;;;;;;get-fake-data;;;;;;;', this.fakeData)
                  
                  this.count = 0;
                  this.time = 0;
                  this.nma = 0;
                  this.fast_name = 0;
                  // this.infoList = [];
                  //console.log('init context: ', context);
                  //console.log(this.count);
                  this._context = context;
                  this._input = inputCallback;
                  var symbol = 'BTC';
                  // var symbol = PineJS.Std.ticker(this._context); // 获取所选商品代码
                  this._context.new_sym(symbol, PineJS.Std.period(this._context), PineJS.Std.period(this._context));
              };

              this.main = function (context, inputCallback) {
                  this.count += 1;
                  // 时间的计算和8小时的时区问题
                  var t = this._context['symbol']['time'] / 1000;

                  if(this.count > 5 && this.count < 10){
                    // 只显示几个示例数据
                    console.log('fakeData', this.fakeData);
                    console.log('symbol-time:', t, this._context['symbol']['time']);
                  }
                  // console.log('count: ',this.count, this.time);
                  
                  //if(this.count<5)console.log('main fakeData: ', this.fakeData[this.count]);
                  this._context = context;
                  this._input = inputCallback;
                  this._context.select_sym(1);

                  // console.log('this-nma:', t, this.nma)
                  if(this.count > 10 && this.fakeData && this.fakeData.hasOwnProperty(t)){
                    this.nma = this.fakeData[t]['nma'];
                    this.fast_nma = this.fakeData[t]['fast_nma'];
                    return [this.nma, this.fast_nma];
                    // console.log('this-nma:', t, this.nma)
                  }

                  return [this.nma, this.fast_nma];
              }
          }
        },

        // 新定义NMM一个指标
        {
          name: 'NMM',
          metainfo: {
              '_metainfoVersion': 40,
              'id': 'NMM@tv-basicstudies-1',
              'scriptIdPart': '',
              'name': 'NMM',
              //当调用createStudy方法时，它也被用作“name”参数
              'description': 'NMM',
              // 该描述将显示在图表上
              'shortDescription': 'NMM',
              'is_hidden_study': false,
              // 指标曲线是否在主数据列窗口中显示
              'is_price_study': false,
              'isCustomIndicator': true,
              'plots': [{
                  'id': 'plot_0',
                  'type': 'line'
              },
              {
                  'id': 'plot_1',
                  'type': 'line'
              },
              ],
              'defaults': {
                  'styles': {
                      'plot_0': {
                          'linestyle': 0,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 2, // 绘制类型为线形图： 2
                          'trackPrice': false,
                          'transparency': 10,
                          'color': '#008B45'
                      },
                      'plot_1':{
                          'linestyle': 2,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 7,
                          'trackPrice': false,
                          'transparency': 60,
                          'color': '#FFA500'
                      }
                  },
                  'precision': 2, // 精度 eg：608.4
                  'inputs': {}
              },
              'styles': {
                  'plot_0': {
                      'title': 'NMM',
                      'histogrambase': 0,
                  },
              },
              'inputs': [],
          },
          constructor: function () {
              this.init = function (context, inputCallback) {
                  var fakeDataRSI = [];
                  let sym = tvWidget.activeChart().symbol()
                  let freq = tvWidget.activeChart().resolution()

                  // 获取指标数据
                  axios
                    .get('http://127.0.0.1:8421/api/get_ocean_ind?resolution='+freq+'&symbol='+sym+'&ind=nmm')
                    .then((res) => {
                        if(res.data.status == 'ok'){
                          fakeDataRSI = res.data.data
                          this.fakeData = fakeDataRSI
                        }
                      }
                    )
                  
                  // this.fakeData = fakeDataRSI;
                  // console.log(';;;;;;;get-fake-data;;;;;;;', this.fakeData)
                  
                  this.count = 0;
                  this.time = 0;
                  this.nmm = 0;
                  // this.infoList = [];
                  //console.log('init context: ', context);
                  //console.log(this.count);
                  this._context = context;
                  this._input = inputCallback;
                  var symbol = 'BTC';
                  // var symbol = PineJS.Std.ticker(this._context); // 获取所选商品代码
                  this._context.new_sym(symbol, PineJS.Std.period(this._context), PineJS.Std.period(this._context));
              };

              this.main = function (context, inputCallback) {
                  this.count += 1;
                  // 时间的计算和8小时的时区问题
                  var t = this._context['symbol']['time'] / 1000;

                  if(this.count > 5 && this.count < 10){
                    // 只显示几个示例数据
                    console.log('fakeData', this.fakeData);
                    console.log('symbol-time:', t, this._context['symbol']['time']);
                  }
                  // console.log('count: ',this.count, this.time);
                  
                  //if(this.count<5)console.log('main fakeData: ', this.fakeData[this.count]);
                  this._context = context;
                  this._input = inputCallback;
                  this._context.select_sym(1);

                  // console.log('this-nmm:', t, this.nmm)
                  if(this.count > 10 && this.fakeData && this.fakeData.hasOwnProperty(t)){
                    this.nmm = this.fakeData[t]['nmm'];
                    return [this.nmm, 0];
                    // console.log('this-nmm:', t, this.nmm)
                  }

                  return [this.nmm, 0];
              }
          }
        },

        // 新定义NMC一个指标
        {
          name: 'NMC',
          metainfo: {
              '_metainfoVersion': 40,
              'id': 'NMC@tv-basicstudies-1',
              'scriptIdPart': '',
              'name': 'NMC',
              //当调用createStudy方法时，它也被用作“name”参数
              'description': 'NMC',
              // 该描述将显示在图表上
              'shortDescription': 'NMC',
              'is_hidden_study': true,
              // 指标曲线是否在主数据列窗口中显示
              'is_price_study': false,
              'isCustomIndicator': true,
              'plots': [{
                  'id': 'plot_0',
                  'type': 'line'
              },
              {
                  'id': 'plot_1',
                  'type': 'line'
              },
              {
                  'id': 'plot_2',
                  'type': 'line'
              },
              ],
              'defaults': {
                  'styles': {
                      'plot_0': {
                          'linestyle': 0,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 2, // 绘制类型为线形图： 2
                          'trackPrice': false,
                          'transparency': 10,
                          'color': '#1E90FF'
                      },
                      'plot_1':{
                          'linestyle': 0,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 7,
                          'trackPrice': false,
                          'transparency': 10,
                          'color': '#F8F8FF'
                      },
                      'plot_2':{
                          'linestyle': 2,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 7,
                          'trackPrice': false,
                          'transparency': 50,
                          'color': '#FF0000'
                      }
                  },
                  'precision': 2, // 精度 eg：608.4
                  'inputs': {}
              },
              'styles': {
                  'plot_0': {
                      'title': 'NMC',
                      'histogrambase': 0,
                  },
              },
              'inputs': [],
          },

          constructor: function () {
              this.init = function (context, inputCallback) {
                  var fakeDataRSI = [];
                  let sym = tvWidget.activeChart().symbol()
                  let freq = tvWidget.activeChart().resolution()

                  // 获取指标数据
                  axios
                    .get('http://127.0.0.1:8421/api/get_ocean_ind?resolution='+freq+'&symbol='+sym+'&ind=nmc')
                    .then((res) => {
                        if(res.data.status == 'ok'){
                          fakeDataRSI = res.data.data
                          this.fakeData = fakeDataRSI
                        }
                      }
                    )
                  
                  // this.fakeData = fakeDataRSI;
                  // console.log(';;;;;;;get-fake-data;;;;;;;', this.fakeData)
                  
                  this.count = 0;
                  this.time = 0;
                  this.nmc = 0;
                  this.nmc_sd = 0;
                  // this.infoList = [];
                  //console.log('init context: ', context);
                  //console.log(this.count);
                  this._context = context;
                  this._input = inputCallback;
                  var symbol = 'BTC';
                  // var symbol = PineJS.Std.ticker(this._context); // 获取所选商品代码
                  this._context.new_sym(symbol, PineJS.Std.period(this._context), PineJS.Std.period(this._context));
              };

              this.main = function (context, inputCallback) {
                  this.count += 1;
                  // 时间的计算和8小时的时区问题
                  // var t = this._context['symbol']['time'] / 1000 + 8 * 3600;
                  var t = this._context['symbol']['time'] / 1000;

                  if(this.count > 5 && this.count < 10){
                    // 只显示几个示例数据
                    console.log('fakeData', this.fakeData);
                    console.log('symbol-time:', t, this._context['symbol']['time']);
                  }
                  // console.log('count: ',this.count, this.time);
                  
                  //if(this.count<5)console.log('main fakeData: ', this.fakeData[this.count]);
                  this._context = context;
                  this._input = inputCallback;
                  this._context.select_sym(1);

                  // console.log('this-NMC:', t, this.NMC)
                  if(this.count > 10 && this.fakeData && this.fakeData.hasOwnProperty(t)){
                    this.nmc = this.fakeData[t]['nmc'];
                    this.nmc_sd = this.fakeData[t]['nmc_sd']
                    return [this.nmc, this.nmc_sd, 0];
                    // console.log('this-nmc:', t, this.nmc)
                  }

                  return [this.nmc, this.nmc_sd, 0];
              }
          }
        },

        // 新定义nms一个指标
        {
          name: 'NMS',
          metainfo: {
              '_metainfoVersion': 40,
              'id': 'NMS@tv-basicstudies-1',
              'scriptIdPart': '',
              'name': 'NMS',
              //当调用createStudy方法时，它也被用作“name”参数
              'description': 'NMS',
              // 该描述将显示在图表上
              'shortDescription': 'NMS',
              'is_hidden_study': true,
              // 指标曲线是否在主数据列窗口中显示
              'is_price_study': false,
              'isCustomIndicator': true,
              'plots': [{
                  'id': 'plot_0',
                  'type': 'line'
              },
              {
                  'id': 'plot_1',
                  'type': 'line'
              },
              ],
              'defaults': {
                  'styles': {
                      'plot_0': {
                          'linestyle': 0,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 2, // 绘制类型为线形图： 2
                          'trackPrice': false,
                          'transparency': 10,
                          'color': '#008000'
                      },
                      'plot_1':{
                          'linestyle': 2,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 7,
                          'trackPrice': false,
                          'transparency': 60,
                          'color': '#FFA500'
                      }
                  },
                  'precision': 2, // 精度 eg：608.4
                  'inputs': {}
              },
              'styles': {
                  'plot_0': {
                      'title': 'nms',
                      'histogrambase': 0,
                  },
              },
              'inputs': [],
          },
          constructor: function () {
              this.init = function (context, inputCallback) {
                  var fakeDataRSI = [];
                  let sym = tvWidget.activeChart().symbol()
                  let freq = tvWidget.activeChart().resolution()

                  // 获取指标数据
                  axios
                    .get('http://127.0.0.1:8421/api/get_ocean_ind?resolution='+freq+'&symbol='+sym+'&ind=nms')
                    .then((res) => {
                        if(res.data.status == 'ok'){
                          fakeDataRSI = res.data.data
                          this.fakeData = fakeDataRSI
                        }
                      }
                    )
                  
                  // this.fakeData = fakeDataRSI;
                  // console.log(';;;;;;;get-fake-data;;;;;;;', this.fakeData)
                  
                  this.count = 0;
                  this.time = 0;
                  this.nms = 0;
                  // this.infoList = [];
                  //console.log('init context: ', context);
                  //console.log(this.count);
                  this._context = context;
                  this._input = inputCallback;
                  var symbol = 'BTC';
                  // var symbol = PineJS.Std.ticker(this._context); // 获取所选商品代码
                  this._context.new_sym(symbol, PineJS.Std.period(this._context), PineJS.Std.period(this._context));
              };

              this.main = function (context, inputCallback) {
                  this.count += 1;
                  // 时间的计算和8小时的时区问题
                  // var t = this._context['symbol']['time'] / 1000 + 8 * 3600;
                  var t = this._context['symbol']['time'] / 1000;

                  if(this.count > 5 && this.count < 10){
                    // 只显示几个示例数据
                    console.log('fakeData', this.fakeData);
                    console.log('symbol-time:', t, this._context['symbol']['time']);
                  }
                  // console.log('count: ',this.count, this.time);
                  
                  //if(this.count<5)console.log('main fakeData: ', this.fakeData[this.count]);
                  this._context = context;
                  this._input = inputCallback;
                  this._context.select_sym(1);

                  // console.log('this-nms:', t, this.nms)
                  if(this.count > 10 && this.fakeData && this.fakeData.hasOwnProperty(t)){
                    this.nms = this.fakeData[t]['nms'];
                    return [this.nms, 0];
                    // console.log('this-nms:', t, this.nms)
                  }

                  return [this.nms, 0];
              }
          }
        },
    
        // 新定义nmc2一个指标
        {
          name: 'NMC2',
          metainfo: {
              '_metainfoVersion': 40,
              'id': 'NMC2@tv-basicstudies-1',
              'scriptIdPart': '',
              'name': 'NMC2',
              //当调用createStudy方法时，它也被用作“name”参数
              'description': 'NMC2',
              // 该描述将显示在图表上
              'shortDescription': 'NMC2',
              'is_hidden_study': true,
              // 指标曲线是否在主数据列窗口中显示
              'is_price_study': false,
              'isCustomIndicator': true,
              'plots': [{
                  'id': 'plot_0',
                  'type': 'line'
              },
              {
                  'id': 'plot_1',
                  'type': 'line'
              },
              {
                  'id': 'plot_2',
                  'type': 'line'
              },
              ],
              'defaults': {
                  'styles': {
                      'plot_0': {
                          'linestyle': 0,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 2, // 绘制类型为线形图： 2
                          'trackPrice': false,
                          'transparency': 10,
                          'color': '#87CEFA'
                      },
                      'plot_1':{
                          'linestyle': 0,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 7,
                          'trackPrice': false,
                          'transparency': 10,
                          'color': '#F8F8FF'
                      },
                      'plot_2': {
                        'linestyle': 2,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 7,
                          'trackPrice': false,
                          'transparency': 50,
                          'color': '#FF0000'
                      }
                  },
                  'precision': 2, // 精度 eg：608.4
                  'inputs': {}
              },
              'styles': {
                  'plot_0': {
                      'title': 'nmc2',
                      'histogrambase': 0,
                  },
              },
              'inputs': [],
          },
          
          constructor: function () {
              this.init = function (context, inputCallback) {
                  var fakeDataRSI = [];
                  let sym = tvWidget.activeChart().symbol()
                  let freq = tvWidget.activeChart().resolution()

                  // 获取指标数据
                  axios
                    .get('http://127.0.0.1:8421/api/get_ocean_ind?resolution='+freq+'&symbol='+sym+'&ind=nmc2')
                    .then((res) => {
                        if(res.data.status == 'ok'){
                          fakeDataRSI = res.data.data
                          this.fakeData = fakeDataRSI
                        }
                      }
                    )
                  
                  // this.fakeData = fakeDataRSI;
                  // console.log(';;;;;;;get-fake-data;;;;;;;', this.fakeData)
                  
                  this.count = 0;
                  this.time = 0;
                  this.nmc2 = 0;
                  this.nmc2_sd = 0;
                  // this.infoList = [];
                  //console.log('init context: ', context);
                  //console.log(this.count);
                  this._context = context;
                  this._input = inputCallback;
                  var symbol = 'BTC';
                  // var symbol = PineJS.Std.ticker(this._context); // 获取所选商品代码
                  this._context.new_sym(symbol, PineJS.Std.period(this._context), PineJS.Std.period(this._context));
              };

              this.main = function (context, inputCallback) {
                  this.count += 1;
                  // 时间的计算和8小时的时区问题
                  // var t = this._context['symbol']['time'] / 1000 + 8 * 3600;
                  var t = this._context['symbol']['time'] / 1000;

                  if(this.count > 5 && this.count < 10){
                    // 只显示几个示例数据
                    console.log('fakeData', this.fakeData);
                    console.log('symbol-time:', t, this._context['symbol']['time']);
                  }
                  // console.log('count: ',this.count, this.time);
                  
                  //if(this.count<5)console.log('main fakeData: ', this.fakeData[this.count]);
                  this._context = context;
                  this._input = inputCallback;
                  this._context.select_sym(1);

                  // console.log('this-nmc2:', t, this.nmc2)
                  if(this.count > 10 && this.fakeData && this.fakeData.hasOwnProperty(t)){
                    this.nmc2 = this.fakeData[t]['nmc2'];
                    this.nmc2_sd = this.fakeData[t]['nmc2_sd']
                    return [this.nmc2, this.nmc2_sd, 0];
                    // console.log('this-nmc2:', t, this.nmc2)
                  }

                  return [this.nmc2, this.nmc2_sd, 0];
              }
          }
        },

        // 新定义NDX一个指标
        {
          name: 'NDX',
          metainfo: {
              '_metainfoVersion': 41,
              'id': 'NDX@tv-basicstudies-1',
              'scriptIdPart': '',
              'name': 'NDX',
              //当调用createStudy方法时，它也被用作“name”参数
              'description': 'NDX',
              // 该描述将显示在图表上
              'shortDescription': 'NDX',
              'is_hidden_study': false,
              // 指标曲线是否在主数据列窗口中显示
              'is_price_study': false,
              'isCustomIndicator': true,
              'plots': [{
                  'id': 'plot_0',
                  'type': 'line'
              }, {'id': 'plot_1',
                  'type': 'hline'
              }, {'id': 'plot_2',
                  'type': 'hline'
              }, {'id': 'plot_3',
                  'type': 'hline'
              },],
              'defaults': {
                  'styles': {
                      'plot_0': {
                          'linestyle': 0,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 2, // 绘制类型为线形图： 2
                          'trackPrice': false,
                          'transparency': 10,
                          'color': '#00FFFF'
                      },  'plot_1': {
                          'linestyle': 2,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 7,
                          'trackPrice': false,
                          'transparency': 50,
                          'color': '#FFFF00'
                      },  'plot_2': {
                          'linestyle': 2,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 7,
                          'trackPrice': false,
                          'transparency': 50,
                          'color': '#FF0000'
                      },  'plot_3': {
                          'linestyle': 2,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 7,
                          'trackPrice': false,
                          'transparency': 50,
                          'color': '#FFFF00'
                      },
                  },
                  'precision': 2, // 精度 eg：608.4
                  'inputs': {}
              },
              'styles': {
                  'plot_0': {
                      'title': 'ndx',
                      'histogrambase': 0,
                  },
              },
              'inputs': [],
          },
          constructor: function () {
              this.init = function (context, inputCallback) {
                  var fakeDataRSI = [];
                  let sym = tvWidget.activeChart().symbol()
                  let freq = tvWidget.activeChart().resolution()

                  // 获取指标数据
                  axios
                    .get('http://127.0.0.1:8421/api/get_ocean_ind?resolution='+freq+'&symbol='+sym+'&ind=ndx')
                    .then((res) => {
                        if(res.data.status == 'ok'){
                          fakeDataRSI = res.data.data
                          this.fakeData = fakeDataRSI
                        }
                      }
                    )
                  
                  // this.fakeData = fakeDataRSI;
                  // console.log(';;;;;;;get-fake-data;;;;;;;', this.fakeData)
                  
                  this.count = 0;
                  this.time = 0;
                  this.ndx = 0;
                  // this.infoList = [];
                  //console.log('init context: ', context);
                  //console.log(this.count);
                  this._context = context;
                  this._input = inputCallback;
                  var symbol = 'BTC';
                  // var symbol = PineJS.Std.ticker(this._context); // 获取所选商品代码
                  this._context.new_sym(symbol, PineJS.Std.period(this._context), PineJS.Std.period(this._context));
              };

              this.main = function (context, inputCallback) {
                  this.count += 1;
                  // 时间的计算和8小时的时区问题
                  // var t = this._context['symbol']['time'] / 1000 + 8 * 3600;
                  var t = this._context['symbol']['time'] / 1000;

                  if(this.count > 5 && this.count < 10){
                    // 只显示几个示例数据
                    console.log('fakeData', this.fakeData);
                    console.log('symbol-time:', t, this._context['symbol']['time']);
                  }
                  // console.log('count: ',this.count, this.time);
                  
                  //if(this.count<5)console.log('main fakeData: ', this.fakeData[this.count]);
                  this._context = context;
                  this._input = inputCallback;
                  this._context.select_sym(1);

                  // console.log('this-ndx:', t, this.ndx)
                  if(this.count > 10 && this.fakeData && this.fakeData.hasOwnProperty(t)){
                    this.ndx = this.fakeData[t]['ndx'];
                    return [this.ndx, 50, 0, -50];
                    // console.log('this-ndx:', t, this.ndx)
                  }

                  return [this.ndx, 50, 0, -50];
              }
          }
        },

        // 新定义NST一个指标
        {
          name: 'NST',
          metainfo: {
              '_metainfoVersion': 41,
              'id': 'NST@tv-basicstudies-1',
              'scriptIdPart': '',
              'name': 'NST',
              //当调用createStudy方法时，它也被用作“name”参数
              'description': 'NST',
              // 该描述将显示在图表上
              'shortDescription': 'NST',
              'is_hidden_study': false,
              // 指标曲线是否在主数据列窗口中显示
              'is_price_study': false,
              'isCustomIndicator': true,
              'plots': [{
                  'id': 'plot_0',
                  'type': 'line'
              }, {'id': 'plot_1',
                  'type': 'line'
              }, {'id': 'plot_2',
                  'type': 'line'
              }, {'id': 'plot_3',
                  'type': 'line'
              },],
              'defaults': {
                  'styles': {
                      'plot_0': {
                          'linestyle': 0,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 2, // 绘制类型为线形图： 2
                          'trackPrice': false,
                          'transparency': 10,
                          'color': '#F0E68C'
                      },  'plot_1': {
                          'linestyle': 2,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 7,
                          'trackPrice': false,
                          'transparency': 50,
                          'color': '#FFFF00'
                      },  'plot_2': {
                          'linestyle': 2,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 7,
                          'trackPrice': false,
                          'transparency': 60,
                          'color': '#FF0000'
                      },  'plot_3': {
                          'linestyle': 2,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 7,
                          'trackPrice': false,
                          'transparency': 60,
                          'color': '#FFFF00'
                      },
                  },
                  'precision': 2, // 精度 eg：608.4
                  'inputs': {}
              },
              'styles': {
                  'plot_0': {
                      'title': 'nst',
                      'histogrambase': 0,
                  },
              },
              'inputs': [],
          },
          constructor: function () {
              this.init = function (context, inputCallback) {
                  var fakeDataRSI = [];
                  let sym = tvWidget.activeChart().symbol()
                  let freq = tvWidget.activeChart().resolution()

                  // 获取指标数据
                  axios
                    .get('http://127.0.0.1:8421/api/get_ocean_ind?resolution='+freq+'&symbol='+sym+'&ind=nst')
                    .then((res) => {
                        if(res.data.status == 'ok'){
                          fakeDataRSI = res.data.data
                          this.fakeData = fakeDataRSI
                        }
                      }
                    )

                  // this.fakeData = fakeDataRSI;
                  // console.log(';;;;;;;get-fake-data;;;;;;;', this.fakeData)
                  
                  this.count = 0;
                  this.time = 0;
                  this.nst = 0;
                  // this.infoList = [];
                  //console.log('init context: ', context);
                  //console.log(this.count);
                  this._context = context;
                  this._input = inputCallback;
                  var symbol = 'BTC';
                  // var symbol = PineJS.Std.ticker(this._context); // 获取所选商品代码
                  this._context.new_sym(symbol, PineJS.Std.period(this._context), PineJS.Std.period(this._context));
              };

              this.main = function (context, inputCallback) {
                  this.count += 1;
                  var t = this._context['symbol']['time'] / 1000;

                  if(this.count > 5 && this.count < 10){
                    // 只显示几个示例数据
                    console.log('fakeData', this.fakeData);
                    console.log('symbol-time:', t, this._context['symbol']['time']);
                  }
                  // console.log('count: ',this.count, this.time);
                  
                  //if(this.count<5)console.log('main fakeData: ', this.fakeData[this.count]);
                  this._context = context;
                  this._input = inputCallback;
                  this._context.select_sym(1);

                  // console.log('this-nst:', t, this.nst)
                  if(this.count > 10 && this.fakeData && this.fakeData.hasOwnProperty(t)){
                    this.nst = this.fakeData[t]['nst'];
                    return [this.nst, 50, 0, -50];
                    // console.log('this-nst:', t, this.nst)
                  }

                  return [this.nst, 50, 0, -50];
              }
          }
        },

        // 组合NDX和NST在一个图上显示
        {
          name: 'NDX_NST',
          metainfo: {
              '_metainfoVersion': 42,
              'id': 'NDX_NST@tv-basicstudies-1',
              'scriptIdPart': '',
              'name': 'NDX_NST',
              //当调用createStudy方法时，它也被用作“name”参数
              'description': 'NDX_NST',
              // 该描述将显示在图表上
              'shortDescription': 'NDX_NST',
              'is_hidden_study': false,
              // 指标曲线是否在主数据列窗口中显示
              'is_price_study': false,
              'isCustomIndicator': true,
              'plots': [{
                  'id': 'plot_0',
                  'type': 'line'
              }, {'id': 'plot_1',
                  'type': 'line'
              }, {'id': 'plot_2',
                  'type': 'line'
              }, {'id': 'plot_3',
                  'type': 'line'
              }, {'id': 'plot_4',
                  'type': 'line'
              },
              ],
              'defaults': {
                  'styles': {
                    'plot_0': {
                          'linestyle': 0,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 2, // 绘制类型为线形图： 2
                          'trackPrice': false,
                          'transparency': 10,
                          'color': '#00FFFF'
                      },
                      'plot_1': {
                          'linestyle': 0,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 2, // 绘制类型为线形图： 2
                          'trackPrice': false,
                          'transparency': 10,
                          'color': '#F0E68C'
                      },  
                      'plot_2': {
                          'linestyle': 2,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 7,
                          'trackPrice': false,
                          'transparency': 50,
                          'color': '#FFFF00'
                      },  'plot_3': {
                          'linestyle': 2,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 7,
                          'trackPrice': false,
                          'transparency': 60,
                          'color': '#FF0000'
                      },  'plot_4': {
                          'linestyle': 2,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 7,
                          'trackPrice': false,
                          'transparency': 60,
                          'color': '#FFFF00'
                      },
                  },
                  'precision': 2, // 精度 eg：608.4
                  'inputs': {}
              },
              'styles': {
                  'plot_0': {
                      'title': 'NDX_NST',
                      'histogrambase': 0,
                  },
              },
              'inputs': [],
          },
          constructor: function () {
              this.init = function (context, inputCallback) {
                  var fakeDataRSI = [];
                  let sym = tvWidget.activeChart().symbol()
                  let freq = tvWidget.activeChart().resolution()

                  // 获取指标数据
                  axios
                    .get('http://127.0.0.1:8421/api/get_ocean_ind?resolution='+freq+'&symbol='+sym+'&ind=ndx_nst')
                    .then((res) => {
                        if(res.data.status == 'ok'){
                          fakeDataRSI = res.data.data
                          this.fakeData = fakeDataRSI
                        }
                      }
                    )

                  // this.fakeData = fakeDataRSI;
                  // console.log(';;;;;;;get-fake-data;;;;;;;', this.fakeData)
                  
                  this.count = 0;
                  this.time = 0;
                  this.ndx = 0;
                  this.nst = 0;
                  // this.infoList = [];
                  //console.log('init context: ', context);
                  //console.log(this.count);
                  this._context = context;
                  this._input = inputCallback;
                  var symbol = 'BTC';
                  // var symbol = PineJS.Std.ticker(this._context); // 获取所选商品代码
                  this._context.new_sym(symbol, PineJS.Std.period(this._context), PineJS.Std.period(this._context));
              };

              this.main = function (context, inputCallback) {
                  this.count += 1;
                  var t = this._context['symbol']['time'] / 1000;

                  if(this.count > 5 && this.count < 10){
                    // 只显示几个示例数据
                    console.log('fakeData', this.fakeData);
                    console.log('symbol-time:', t, this._context['symbol']['time']);
                  }
                  // console.log('count: ',this.count, this.time);
                  
                  //if(this.count<5)console.log('main fakeData: ', this.fakeData[this.count]);
                  this._context = context;
                  this._input = inputCallback;
                  this._context.select_sym(1);

                  if(this.count > 10 && this.fakeData && this.fakeData.hasOwnProperty(t)){
                    this.ndx = this.fakeData[t]['ndx'];
                    this.nst = this.fakeData[t]['nst'];
                    return [this.ndx, this.nst, 50, 0, -50];
                  }

                  return [this.ndx, this.nst, 50, 0, -50];
              }
          }
        },

        // 新定义NXC一个指标
        {
          name: 'NXC',
          metainfo: {
              '_metainfoVersion': 41,
              'id': 'NXC@tv-basicstudies-1',
              'scriptIdPart': '',
              'name': 'NXC',
              //当调用createStudy方法时，它也被用作“name”参数
              'description': 'NXC',
              // 该描述将显示在图表上
              'shortDescription': 'NXC',
              'is_hidden_study': false,
              // 指标曲线是否在主数据列窗口中显示
              'is_price_study': false,
              'isCustomIndicator': true,
              'plots': [{
                  'id': 'plot_0',
                  'type': 'line'
              }, {'id': 'plot_1',
                  'type': 'hline'
              }, {'id': 'plot_2',
                  'type': 'hline'
              }, {'id': 'plot_3',
                  'type': 'hline'
              },],
              'defaults': {
                  'styles': {
                      'plot_0': {
                          'linestyle': 0,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 2, // 绘制类型为线形图： 2
                          'trackPrice': false,
                          'transparency': 10,
                          'color': '#00FF00'
                      },  'plot_1': {
                          'linestyle': 2,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 7,
                          'trackPrice': false,
                          'transparency': 50,
                          'color': '#FFFF00'
                      },  'plot_2': {
                          'linestyle': 2,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 7,
                          'trackPrice': false,
                          'transparency': 60,
                          'color': '#FF0000'
                      },  'plot_3': {
                          'linestyle': 2,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 7,
                          'trackPrice': false,
                          'transparency': 60,
                          'color': '#FFFF00'
                      },
                  },
                  'precision': 2, // 精度 eg：608.4
                  'inputs': {}
              },
              'styles': {
                  'plot_0': {
                      'title': 'nxc',
                      'histogrambase': 0,
                  },
              },
              'inputs': [],
          },
          constructor: function () {
              this.init = function (context, inputCallback) {
                  var fakeDataRSI = [];
                  let sym = tvWidget.activeChart().symbol()
                  let freq = tvWidget.activeChart().resolution()

                  // 获取指标数据
                  axios
                    .get('http://127.0.0.1:8421/api/get_ocean_ind?resolution='+freq+'&symbol='+sym+'&ind=nxc')
                    .then((res) => {
                        if(res.data.status == 'ok'){
                          fakeDataRSI = res.data.data
                          this.fakeData = fakeDataRSI
                        }
                      }
                    )
                  
                  // this.fakeData = fakeDataRSI;
                  // console.log(';;;;;;;get-fake-data;;;;;;;', this.fakeData)
                  
                  this.count = 0;
                  this.time = 0;
                  this.nxc = 0;
                  // this.infoList = [];
                  //console.log('init context: ', context);
                  //console.log(this.count);
                  this._context = context;
                  this._input = inputCallback;
                  var symbol = 'BTC';
                  // var symbol = PineJS.Std.ticker(this._context); // 获取所选商品代码
                  this._context.new_sym(symbol, PineJS.Std.period(this._context), PineJS.Std.period(this._context));
              };

              this.main = function (context, inputCallback) {
                  this.count += 1;
                  var t = this._context['symbol']['time'] / 1000;

                  if(this.count > 5 && this.count < 10){
                    // 只显示几个示例数据
                    console.log('fakeData', this.fakeData);
                    console.log('symbol-time:', t, this._context['symbol']['time']);
                  }
                  // console.log('count: ',this.count, this.time);
                  
                  //if(this.count<5)console.log('main fakeData: ', this.fakeData[this.count]);
                  this._context = context;
                  this._input = inputCallback;
                  this._context.select_sym(1);

                  // console.log('this-nxc:', t, this.nxc)
                  if(this.count > 10 && this.fakeData && this.fakeData.hasOwnProperty(t)){
                    this.nxc = this.fakeData[t]['nxc'];
                    return [this.nxc, 50, 0, -50];
                    // console.log('this-nxc:', t, this.nxc)
                  }

                  return [this.nxc, 50, 0, -50];
              }
          }
        },

        // 新定义MSH指标
        {
          name: 'MSH',
          metainfo: {
              '_metainfoVersion': 40,
              'id': 'MSH@tv-basicstudies-1',
              'scriptIdPart': '',
              'name': 'MSH',
              //当调用createStudy方法时，它也被用作“name”参数
              'description': 'MSH',
              // 该描述将显示在图表上
              'shortDescription': 'MSH',
              'is_hidden_study': false,
              // 指标曲线是否在主数据列窗口中显示
              'is_price_study': false,
              'isCustomIndicator': true,
              'plots': [{
                  'id': 'plot_0',
                  'type': 'line'
              },
              {
                  'id': 'plot_1',
                  'type': 'line'
              },
              {
                  'id': 'plot_2',
                  'type': 'line'
              },
              ],
              'defaults': {
                  'styles': {
                      'plot_0': {
                          'linestyle': 0,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 2, // 绘制类型为线形图： 2
                          'trackPrice': false,
                          'transparency': 0,
                          'color': '#008B45'
                      },
                      'plot_1':{
                          'linestyle': 0,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 2,
                          'trackPrice': false,
                          'transparency': 0,
                          'color': '#FF5252'
                      },
                      'plot_2':{
                          'linestyle': 2,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 7,
                          'trackPrice': false,
                          'transparency': 20,
                          'color': '#FFA500'
                      }
                  },
                  'precision': 2, // 精度 eg：608.4
                  'inputs': {}
              },
              'styles': {
                  'plot_0': {
                      'title': 'MSH',
                      'histogrambase': 0,
                  },
              },
              'inputs': [],
          },
          constructor: function () {
              this.init = function (context, inputCallback) {
                  var fakeDataRSI = [];
                  let sym = tvWidget.activeChart().symbol()
                  let freq = tvWidget.activeChart().resolution()

                  // 获取指标数据
                  axios
                    .get('http://127.0.0.1:8421/api/get_mas_ind?resolution='+freq+'&symbol='+sym+'&ind=msh')
                    .then((res) => {
                        if(res.data.status == 'ok'){
                          fakeDataRSI = res.data.data
                          this.fakeData = fakeDataRSI
                        }
                      }
                    )
                  
                  // this.fakeData = fakeDataRSI;
                  // console.log(';;;;;;;get-fake-data;;;;;;;', this.fakeData)
                  
                  this.count = 0;
                  this.dt = 0;
                  this.ma_stick = 0;
                  this.ma_entroy = 0;
                  // this.infoList = [];
                  //console.log('init context: ', context);
                  //console.log(this.count);
                  this._context = context;
                  this._input = inputCallback;
                  var symbol = 'ETH';
                  // var symbol = PineJS.Std.ticker(this._context); // 获取所选商品代码
                  this._context.new_sym(symbol, PineJS.Std.period(this._context), PineJS.Std.period(this._context));
              };

              this.main = function (context, inputCallback) {
                  this.count += 1;
                  // 时间的计算和8小时的时区问题
                  var t = this._context['symbol']['time']/1000;

                  if(this.count > 5 && this.count < 10){
                    // 只显示几个示例数据
                    console.log('fakeData', this.fakeData);
                    console.log('symbol-dt:', t, this._context['symbol']['time']);
                  }
                  // console.log('count: ',this.count, this.time);
                  
                  //if(this.count<5)console.log('main fakeData: ', this.fakeData[this.count]);
                  this._context = context;
                  this._input = inputCallback;
                  this._context.select_sym(1);

                  // console.log('this-nmm:', t, this.nmm)
                  if(this.count > 10 && this.fakeData && this.fakeData.hasOwnProperty(t)){
                    this.ma_stick = this.fakeData[t]['ma_stick'];
                    this.ma_entroy = this.fakeData[t]['ma_entroy'];
                    return [this.ma_stick, this.ma_entroy, 12];
                    console.log('this-nmm:', t, this.ma_stick)
                  }

                  return [this.ma_stick, this.ma_entroy, 12];
              }
          }
        },

        // 新定义MA34XD一个指标
        {
          name: 'MA34XD',
          metainfo: {
              '_metainfoVersion': 40,
              'id': 'MA34XD@tv-basicstudies-1',
              'scriptIdPart': '',
              'name': 'MA34XD',
              //当调用createStudy方法时，它也被用作“name”参数
              'description': 'MA34XD',
              // 该描述将显示在图表上
              'shortDescription': 'MA34XD',
              'is_hidden_study': false,
              // 指标曲线是否在主数据列窗口中显示
              'is_price_study': true,
              'isCustomIndicator': true,
              'plots': [{
                  'id': 'plot_0',
                  'type': 'line'
              },
              ],
              'defaults': {
                  'styles': {
                      'plot_0': {
                          'linestyle': 0,
                          'visible': true,
                          'linewidth': 1,
                          'plottype': 2, // 绘制类型为线形图： 2
                          'trackPrice': false,
                          'transparency': 10,
                          'color': '#008B45'
                      },
                  },
                  'precision': 2, // 精度 eg：608.4
                  'inputs': {}
              },
              'styles': {
                  'plot_0': {
                      'title': 'MA34XD',
                      'histogrambase': 0,
                  },
              },
              'inputs': [],
          },
          constructor: function () {
              this.init = function (context, inputCallback) {
                  var fakeDataRSI = [];
                  let sym = tvWidget.activeChart().symbol()
                  let freq = tvWidget.activeChart().resolution()

                  // 获取指标数据
                  axios
                    .get('http://127.0.0.1:8421/api/get_ma34xd?resolution='+freq+'&symbol='+sym)
                    .then((res) => {
                        if(res.data.status == 'ok'){
                          fakeDataRSI = res.data.data
                          this.fakeData = fakeDataRSI
                        }
                      }
                    )
                  
                  // this.fakeData = fakeDataRSI;
                  // console.log(';;;;;;;get-fake-data;;;;;;;', this.fakeData)
                  
                  this.count = 0;
                  this.time = 0;
                  this.ma34xd = 0;
                  // this.infoList = [];
                  //console.log('init context: ', context);
                  //console.log(this.count);
                  this._context = context;
                  this._input = inputCallback;
                  var symbol = 'BTC';
                  // var symbol = PineJS.Std.ticker(this._context); // 获取所选商品代码
                  this._context.new_sym(symbol, PineJS.Std.period(this._context), PineJS.Std.period(this._context));
              };

              this.main = function (context, inputCallback) {
                  this.count += 1;
                  // 时间的计算和8小时的时区问题
                  var t = this._context['symbol']['time'] / 1000;

                  if(this.count > 5 && this.count < 10){
                    // 只显示几个示例数据
                    console.log('fakeData', this.fakeData);
                    console.log('symbol-time:', t, this._context['symbol']['time']);
                  }
                  // console.log('count: ',this.count, this.time);
                  
                  //if(this.count<5)console.log('main fakeData: ', this.fakeData[this.count]);
                  this._context = context;
                  this._input = inputCallback;
                  this._context.select_sym(1);

                  // console.log('this-nmm:', t, this.nmm)
                  if(this.count > 10 && this.fakeData && this.fakeData.hasOwnProperty(t)){
                    this.ma34xd = this.fakeData[t]['ma34xd'];
                    return [this.ma34xd];
                    // console.log('this-nmm:', t, this.nmm)
                  }

                  return [this.ma34xd];
              }
          }
        },

        ]);
      },
    };

    const tvWidget = new widget(widgetOptions);
    this.tvWidget = tvWidget;
    var bi_list = 'bi';
    var xd_list = 'xd';
    var zs_list = 'zs';
    // var ffx_list = 'father_fx';
    // var gfx_list = 'grandpa_fx';
    // var ma5ma34_xd = '';

    // 定义一个变量，用来存放线段的数据
    // var xds: string[] = []

    this.bi_list = bi_list;

    window.bi_list = this.bi_list
    window.zs_list = zs_list

    // console.log('bi-list-for-table');
    // console.table(bi_list);
    window.axios = axios 

    // 可以在console里面调试
    // window.this = this
    // window.info = this.info
    window.tvWidget = this.tvWidget

    tvWidget.onChartReady(() => {
      // tvWidget.chart().createShape(
			// 	{ 
			// 		time: Date.parse('2017-12-05')/1000
			// 	}, 
			// 	{
			// 		shape: 'vertical_line',
			// 		overrides: {
			// 			'color': '#C71585',
			// 		}
			// 	}
      // );

      // 自定义菜单项目
      // tvWidget.onContextMenu(function(unixtime, price) {
      //   return [{
      //       position: "top",
      //       text: "First top menu item, time: " + unixtime + ", price: " + price,
      //       click: function() { alert("First clicked."); }
      //   },
      //   { text: "-", position: "top" },
      //   { text: "-Objects Tree..." },
      //   {
      //       position: "top",
      //       text: "Second top menu item 2",
      //       click: function() { alert("Second clicked."); }
      //   }, {
      //       position: "bottom",
      //       text: "Bottom menu item",
      //       click: function() { alert("Third clicked."); }
      //   }];
      // });

      tvWidget.onShortcut("alt+z", function() {
        tvWidget.executeActionById("drawing");
      });

      tvWidget.activeChart().onDataLoaded().subscribe(
        null,
        () => console.log('baihuo: New history bars are loaded'),
        true
      );

      tvWidget.activeChart().dataReady(() => {
        console.log('baihuo: data ready.');

        // 隐藏画图工具栏
        // tvWidget.chart().executeActionById("drawingToolbarAction");
      });

      // tvWidget.activeChart().crossHairMoved(({ time, price }) => console.log('baihuo:', time, price));

      tvWidget.headerReady().then(() => {

        /*
          // 获取信息
          const btn_chart = tvWidget.createButton();
          btn_chart.setAttribute('title', '显示调试的信息');
          btn_chart.classList.add('apply-common-tooltip');
          btn_chart.addEventListener('click', function(){
            let cnt = tvWidget.chartsCount();
            console.log('###baihuo: chart-count:', cnt, tvWidget.layoutName());
            console.log('###baihuo: visible-range:', tvWidget.activeChart().getVisibleRange());
            console.log('###baihuo: resolution:', tvWidget.activeChart().resolution());
          });
          btn_chart.innerHTML = 'get info';

          // 导出数据
          const btn_exp = tvWidget.createButton();
          btn_exp.setAttribute('title', '此处是导出数据，导出了什么呢？');
          btn_exp.classList.add('apply-common-tooltip');
          btn_exp.addEventListener('click', function(){
            // 问题：导出了什么呢？
            tvWidget.activeChart().exportData({ includeTime: false, includeSeries: true, from: Date.UTC(2020, 8, 1) / 1000, to: Date.UTC(2020, 8, 2) / 1000 });
          });
          btn_exp.innerHTML = 'export';
        */

        /* 窗口个数 */
        // const btn_win = tvWidget.createButton();
        // btn_win.setAttribute('title', 'Click to show a notification popup');
        // btn_win.classList.add('apply-common-tooltip');
        // btn_win.addEventListener('click', function(){
        //   tvWidget.setLayout('4h');
        //   console.log(tvWidget.layout());
        // });
        // btn_win.innerHTML = '布局';
        
        // 创建一个跳转的按钮
        // const btn2 = tvWidget.createButton();
        // btn2.setAttribute('title', '跳跃到这个时间段');
        // btn2.classList.add('apply-common-tooltip');
        // btn2.addEventListener('click', () => tvWidget.activeChart().setVisibleRange(
        //   { from: Date.parse('2007-01-10 0:0:0')/1000, to: Date.parse('2007-12-31 13:0:0')/1000 },
        //   { percentRightMargin: 20 }
        //   ).then(() => console.log('baihuo: New visible range is applied')));
        // btn2.innerHTML = '时间段';


        // 上级别的分型
        // const btn_father_fx = tvWidget.createButton();
        // btn_father_fx.setAttribute('title', '画出上级别的分型');
        // btn_father_fx.classList.add('apply-common-tooltip');
        // btn_father_fx.addEventListener('click', function(){
        //   let sym = tvWidget.activeChart().symbol()
        //   let freq = tvWidget.activeChart().resolution()
        //   axios
        //     .get('http://127.0.0.1:8421/api/get_upper_fx?fx_jibie=father&resolution='+freq+'&symbol='+sym)
        //     .then(function(res){
        //       console.log(';;;;;;;;get_upper_fx;;;;;;;;;;;;;');
        //       bi_list = res.data.data;
        //       console.table(bi_list);
        //       for (let item of bi_list) {
        //         var start_dt = item['start_dt']
        //         var end_dt = item['end_dt']
        //         var low = item['low']
        //         var high = item['high']

        //         var bgcolor = '#BA55D3'

        //         tvWidget.chart(0).createMultipointShape(
        //           [{time: Date.parse(start_dt)/1000, price: low},
        //           {time: Date.parse(end_dt)/1000, price: high},],
        //           {
        //               shape: 'rectangle',
        //               // lock: true,
        //               // disableSelection: true,
        //               // disableSave: true,
        //               // disableUndo: true,
        //               overrides: {
        //                   'transparency': 85,
        //                   'linewidth': 1,
        //                   'color': '#4B0082',
        //                   'backgroundColor': bgcolor,
        //               }
        //           }
        //         );
        //       }                
        //     });
        // });
        // btn_father_fx.innerHTML = '上级分型';

        // K线顶底
        const btn_xd_fx = tvWidget.createButton();
        btn_xd_fx.setAttribute('title', 'K顶底');
        btn_xd_fx.classList.add('apply-common-tooltip');
        btn_xd_fx.addEventListener('click', function(){
          let sym = tvWidget.activeChart().symbol()
          let freq = tvWidget.activeChart().resolution()
          axios
            .get('http://127.0.0.1:8421/api/bzxd_mark?mtype=kline_dg&tf='+freq+'&symbol='+sym)
            .then((resp) => {
              let bi_list = resp.data.data;
              console.log(';;;;;;;get-xd_xxk;;;;;;;')
              console.table(bi_list)
              for(var item of bi_list){
                let dt = item['dt']
                let dg_type = item['vtype']
                let status = item['status']
                if(dg_type =='high'){
                  let chr = 'g';
                  if(status == 'merged'){
                    chr = '-mg'
                  }else if(status =='extended'){
                    chr = '-sg'
                  }else if(status == 'divergence'){
                    chr = '-bsg'
                  }
                    tvWidget.chart(0).createShape(
                        {time: Date.parse(dt)/1000, channel: 'high'}, 
                            {
                            shape: 'arrow_down',
                            text: chr,
                            overrides: {
                                'color': '#1E90FF'
                            }
                        }
                    );
                }else if(dg_type =='low'){
                  let chr = 'd';
                  if(status == 'merged'){
                    chr = '-md'
                  }else if(status =='extended'){
                    chr = '-sd'
                  }else if(status == 'divergence'){
                    chr = '-bsg'
                  }
                  tvWidget.chart(0).createShape(
                        {time: Date.parse(dt)/1000, channel: 'low'},
                            {
                            shape: 'arrow_up',
                            text: chr,
                            overrides: {
                                'color': '#1E90FF'
                            }
                        }
                    ); 
                }
              }
            });
        });
        btn_xd_fx.innerHTML = '<font color="#1E90FF">K顶底</font>';

        // ma5顶底
        const btn_xd_mafx = tvWidget.createButton();
        btn_xd_mafx.setAttribute('title', 'ma5顶底');
        btn_xd_mafx.classList.add('apply-common-tooltip');
        btn_xd_mafx.addEventListener('click', function(){
          let sym = tvWidget.activeChart().symbol()
          let freq = tvWidget.activeChart().resolution()
          axios
            .get('http://127.0.0.1:8421/api/bzxd_mark?mtype=ma5_dg&tf='+freq+'&symbol='+sym)
            .then((resp) => {
              let bi_list = resp.data.data;
              console.log(';;;;;;;get-xd_xxk;;;;;;;')
              console.table(bi_list)
              for(var item of bi_list){
                let dt = item['dt']
                let dg_type = item['ma5_dg']
                if(dg_type =='g'){
                    tvWidget.chart(0).createShape(
                        {time: Date.parse(dt)/1000, channel: 'high'}, 
                            {
                            shape: 'arrow_down',
                            text: 'g',
                            overrides: {
                                'color': '#FFFFE0'
                            }
                        }
                    );
                }else if(dg_type =='d'){
                  tvWidget.chart(0).createShape(
                        {time: Date.parse(dt)/1000, channel: 'low'},
                            {
                            shape: 'arrow_up',
                            text: 'd',
                            overrides: {
                                'color': '#FFFFE0'
                            }
                        }
                    ); 
                }
              }
            });
        });
        btn_xd_mafx.innerHTML = '<font color="#FFFFE0">ma5顶底</font>';

        // 所有的转折K
        const btn_xd_zzk = tvWidget.createButton();
        btn_xd_zzk.setAttribute('title', '转折K');
        btn_xd_zzk.classList.add('apply-common-tooltip');
        btn_xd_zzk.addEventListener('click', function(){
          let sym = tvWidget.activeChart().symbol()
          let freq = tvWidget.activeChart().resolution()
          axios
            .get('http://127.0.0.1:8421/api/bzxd_mark?mtype=zzk&tf='+freq+'&symbol='+sym)
            .then((resp) => {
              let bi_list = resp.data.data;
              console.log(';;;;;;;get-xd_xxk;;;;;;;')
              console.table(bi_list)
              for(var item of bi_list){
                let dt = item['dt']
                let direction = item['direction']
                let low = item['low']
                let high = item['high']
                if(direction =='down'){
                    tvWidget.chart(0).createShape(
                        {time: Date.parse(dt)/1000, price: high * 1.005}, 
                            {
                            shape: 'icon',
                            text: 'z',
                            overrides: {
                                'color': '#00FFFF',
                                'icon': '0xf107',
                                'size': 25,
                            }
                        }
                    );
                }else if(direction =='up'){
                  tvWidget.chart(0).createShape(
                        {time: Date.parse(dt)/1000, price: low * 0.995},
                            {
                            shape: 'icon',
                            text: 'z',
                            overrides: {
                                'color': '#00FFFF',
                                'icon': '0xf106',
                                'size': 25,
                            }
                        }
                    ); 
                }
              }
            });
        });
        btn_xd_zzk.innerHTML = '<font color="#00FFFF">转折K</font>';
        

        // // 本质线段的转折K
        // const btn_bzxd_zzk = tvWidget.createButton();
        // btn_bzxd_zzk.setAttribute('title', '本质转折K');
        // btn_bzxd_zzk.classList.add('apply-common-tooltip');
        // btn_bzxd_zzk.addEventListener('click', function(){
        //   let sym = tvWidget.activeChart().symbol()
        //   let freq = tvWidget.activeChart().resolution()
        //   axios
        //     .get('http://127.0.0.1:8421/api/bzzs_mark?mtype=bzxd_zzk&tf='+freq+'&symbol='+sym)
        //     .then((resp) => {
        //       let bi_list = resp.data.data;
        //       console.log(';;;;;;;get-xd_xxk;;;;;;;')
        //       console.table(bi_list)
        //       for(var item of bi_list){
        //         let dt = item['dt']
        //         let direction = item['direction']
        //         let low = item['low']
        //         let high = item['high']
        //         if(direction =='down'){
        //             tvWidget.chart(0).createShape(
        //                 {time: Date.parse(dt)/1000, price: high * 1.002}, 
        //                     {
        //                     shape: 'icon',
        //                     text: 'z',
        //                     overrides: {
        //                         'color': '#FF69B4',
        //                         'icon': '0xf107',
        //                         'size': 25,
        //                     }
        //                 }
        //             );
        //         }else if(direction =='up'){
        //           tvWidget.chart(0).createShape(
        //                 {time: Date.parse(dt)/1000, price: low * 0.998},
        //                     {
        //                     shape: 'icon',
        //                     text: 'z',
        //                     overrides: {
        //                         'color': '#FF69B4',
        //                         'icon': '0xf106',
        //                         'size': 25,
        //                     }
        //                 }
        //             ); 
        //         }
        //       }
        //     });
        // });
        // btn_bzxd_zzk.innerHTML = '<font color="#FF69B4">本质转折K</font>';

        // 中枢线
        const btn_zs_line = tvWidget.createButton();
        btn_zs_line.setAttribute('title', '中枢线');
        btn_zs_line.classList.add('apply-common-tooltip');
        btn_zs_line.addEventListener('click', function(){
          let sym = tvWidget.activeChart().symbol()
          let tf = tvWidget.activeChart().resolution()
          axios
            .get('http://127.0.0.1:8421/api/bzxd_mark?mtype=zs_line&tf='+tf+'&symbol='+sym)
            .then((res) => {
              console.log(';;;;;;;;get-cross-bi-list;;;;;;;;;;;;;');
              this.bi_list = res.data.data;
              console.table(this.bi_list)
              for (var _i = 0; _i < this.bi_list.length; _i++) {
                let start = this.bi_list[_i]['dt'];
                let end = this.bi_list[_i]['dt'];
                let zs_line = this.bi_list[_i]['value'];
                let heiK = this.bi_list[_i]['heiK']
                let direction = this.bi_list[_i]['direction']
                let low = this.bi_list[_i]['low']
                let high = this.bi_list[_i]['high']
                let status = this.bi_list[_i]['status']

                // console.log(start, end, start_type, end_type)

                let color = '#00FFFF'
                if(direction == 'down'){
                  color = '#FF0000'
                }

                // 默认虚线
                let linestyle = 1

                // 有heiK的，使用实线
                if (heiK != '-'){
                  linestyle = 0
                }

                let zsl_icon = '0xf120';
                if(status != 'ok'){
                  zsl_icon = '0xf121'
                }

                // 表示中枢线的位置和方向
                if(direction =='down'){
                    tvWidget.chart(0).createShape(
                        {time: Date.parse(start)/1000, price: zs_line * 1.002},
                        // {time: Date.parse(start)/1000, price: high},
                            {
                            shape: 'icon',
                            // lock: true,
                            disableSelection: true,
                            overrides: {
                                'color': color,
                                'icon': zsl_icon,
                                'size': 18,
                            }
                        }
                    );
                    if(heiK!='-'){
                      // 表示黑K的位置
                      tvWidget.chart(0).createShape(
                          {time: Date.parse(heiK)/1000, channel: 'high'},
                              {
                              shape: 'icon',
                              // lock: true, 锁定后，无法通过界面的按钮删除
                              disableSelection: true,
                              overrides: {
                                  'color': '#696969',
                                  'icon': '0xf0e3',
                                  'size': 18,
                              }
                          }
                      );
                    }
                }else if(direction =='up'){
                  tvWidget.chart(0).createShape(
                        {time: Date.parse(start)/1000, price: zs_line * 0.998}, 
                        // {time: Date.parse(start)/1000, price: low}, 
                            {
                            shape: 'icon',
                            // lock: true,
                            disableSelection: true,
                            overrides: {
                                'color': color,
                                'icon': zsl_icon,
                                'size': 18,
                            }
                        }
                    );
                    if(heiK!='-'){
                      // 表示黑K的位置
                      tvWidget.chart(0).createShape(
                          {time: Date.parse(heiK)/1000, channel: 'low'},
                              {
                              shape: 'icon',
                              // lock: true,锁定后，无法通过界面的按钮删除
                              disableSelection: true,
                              overrides: {
                                  'color': '#696969',
                                  'icon': '0xf0e3',
                                  'size': 18,
                              }
                          }
                      );            
                    }        
                }

                // tvWidget.chart(0).createMultipointShape(
                // [{time: Date.parse(start)/1000, price: zs_line},
                // {time: Date.parse(end)/1000, price: zs_line},],
                // {
                //     shape: 'trend_line',
                //     // lock: true,
                //     // disableSelection: true,
                //     // disableSave: true,
                //     // disableUndo: true,
                //     zOrder: 'top',
                //     overrides: {
                //         'linestyle': linestyle,
                //         'linewidth': 2,
                //         'linecolor': color,
                //     }
                // }
                // );
              }
            });
        });
        btn_zs_line.innerHTML = '<font color="#00FF00">中枢线</font>';

        // 线段中枢
        const btn_xdzs = tvWidget.createButton();
        btn_xdzs.setAttribute('title', '线段中枢');
        btn_xdzs.classList.add('apply-common-tooltip');
        btn_xdzs.addEventListener('click', function(){
          let sym = tvWidget.activeChart().symbol()
          let freq = tvWidget.activeChart().resolution()
          axios
            .get('http://127.0.0.1:8421/api/bzxd_mark?mtype=xdzs&tf='+freq+'&symbol='+sym)
            .then((res) => {
              console.log(';;;;;;;;get-xdzs-list;;;;;;;;;;;;;');
              zs_list = res.data.data;
              console.table(zs_list);

              for (let item of zs_list) {
                var start_dt = item['start_dt']
                var end_dt = item['end_dt']
                var start_price = item['lower']
                var end_price = item['upper']

                var is_nakedeye = item['is_nakedeye'];
                let txt = item['zstext'];

                let trans = 98;
                let color = '#FFFFE0';
                if (is_nakedeye){
                  color = '#00FF00'
                  trans = 85;
                }

                tvWidget.chart(0).createShape(
                {time: Date.parse(start_dt)/1000, price: end_price},
                    {
                    shape: 'text',
                    // lock: true, 锁定后，无法通过界面的按钮删除
                    disableSelection: true,
                    overrides: {
                        'color': color,
                        'text': txt,
                        'fontsize': 15,
                    }
                  }
                );

                tvWidget.chart(0).createMultipointShape(
                [{time: Date.parse(start_dt)/1000, price: start_price},
                {time: Date.parse(end_dt)/1000, price: end_price},],
                {
                    shape: 'rectangle',
                    // lock: true,
                    // disableSelection: true,
                    // disableSave: true,
                    // disableUndo: true,
                    zOrder: 'top',
                    overrides: {
                        'transparency': trans,
                        'linewidth': 1,
                        'color': color,
                        'backgroundColor': '#00FF00',
                    }
                }
                );
              }
            });
        });
        btn_xdzs.innerHTML = '<font color="#FF00FF">XD中枢</font>';

        const btn_bs_point = tvWidget.createButton();
        btn_bs_point.setAttribute('title', '量化买卖');
        btn_bs_point.classList.add('apply-common-tooltip');
        btn_bs_point.addEventListener('click', function(){
          let sym = tvWidget.activeChart().symbol()
          let freq = tvWidget.activeChart().resolution()
          axios
            .get('http://127.0.0.1:8421/api/bzxd_mark?mtype=bspoint&tf='+freq+'&symbol='+sym)
            .then((resp) => {
              let bi_list = resp.data.data;
              console.log(';;;;;;;get-xd_xxk;;;;;;;')
              console.table(bi_list)
              for(var item of bi_list){
                let dt = item['dt']
                let bs_type = item['bstype']
                let low = item['low']
                let high = item['high']
                if(bs_type =='short'){
                    tvWidget.chart(0).createShape(
                        {time: Date.parse(dt)/1000, price: high * 1.03}, 
                            {
                            shape: 'icon',
                            text: '开',
                            overrides: {
                                'color': '#EF534F',
                                'icon': '0xf01a',
                                'size': 20,
                            }
                        }
                    );
                }else if(bs_type =='long'){
                  tvWidget.chart(0).createShape(
                        {time: Date.parse(dt)/1000, price: low * 0.97},
                            {
                            shape: 'icon',
                            text: '开',
                            overrides: {
                                'color': '#27A69A',
                                'icon': '0xf01b',
                                'size': 20,
                            }
                        }
                    ); 
                }
              }
            });
        });
        btn_bs_point.innerHTML = '<font color="#00FFFF">量化买卖</font>';


        // xd： 虚线
        const btn_cross_xd_incr_new = tvWidget.createButton();
        btn_cross_xd_incr_new.setAttribute('title', '本质虚线');
        btn_cross_xd_incr_new.classList.add('apply-common-tooltip');
        btn_cross_xd_incr_new.addEventListener('click', function(){
          let sym = tvWidget.activeChart().symbol()
          let resolution = tvWidget.activeChart().resolution()
          axios
            .get('http://127.0.0.1:8421/api/bzxd_mark?mtype=xd_dg_extended&tf='+resolution+'&symbol='+sym)
            .then((res) => {
              console.log(';;;;;;;;get-cross-bi-list;;;;;;;;;;;;;');
              bi_list = res.data.data;
              console.table(bi_list)

              let j=0;
              for (var i = 0; i < bi_list.length-1; i++) {
                let start = bi_list[i]['dt'];
                let start_type = bi_list[i]['vtype']
                let start_status = bi_list[i]['status'];
                let before_has_zs = bi_list[i]['before_has_zs'];
                let after_has_zs = bi_list[i]['after_has_zs'];

                j = i+1

                let end = bi_list[j]['dt'];
                let end_type = bi_list[j]['vtype']
                let end_status = bi_list[j]['status'];
                console.log(start, end, start_type, end_type)

                let color = '#DDA0DD'
                let linestyle = 1

                if(start_status=='extended' || end_status =='extended' || start_status=='divergence' || end_status =='divergence' || start_status=='divergence' || end_status =='divergence'){
                  if (! before_has_zs || ! after_has_zs){
                    linestyle = 2;
                  }

                  tvWidget.chart(0).createMultipointShape(
                  [{time: Date.parse(start)/1000, channel: start_type},
                  {time: Date.parse(end)/1000, channel: end_type},],
                  {
                      shape: 'trend_line',
                      // lock: true,
                      // disableSelection: true,
                      // disableSave: true,
                      // disableUndo: true,
                      overrides: {
                          'linestyle': linestyle,
                          'linewidth': 1,
                          'linecolor': color,
                      }
                  }
                  );
                }
              }
            });
        });
        btn_cross_xd_incr_new.innerHTML = '<font color="#DDA0DD">本质虚线</font>';

        // xd： 本质线段
        const btn_essence_xd = tvWidget.createButton();
        btn_essence_xd.setAttribute('title', '本质线段');
        btn_essence_xd.classList.add('apply-common-tooltip');
        btn_essence_xd.addEventListener('click', function(){
          let sym = tvWidget.activeChart().symbol()
          let resolution = tvWidget.activeChart().resolution()
          axios
            .get('http://127.0.0.1:8421/api/bzxd_mark?mtype=xd_dg&tf='+resolution+'&symbol='+sym)
            .then((res) => {
              console.log(';;;;;;;;get-cross-bi-list;;;;;;;;;;;;;');
              bi_list = res.data.data;
              console.table(bi_list)

              let linestyle = 0 
              let j = 0;

              for (var i = 0; i < bi_list.length-1; i++) {
                
                let start = bi_list[i]['dt'];
                let start_type = bi_list[i]['vtype']
                let start_status = bi_list[i]['status'];

                j = i+1

                let end = bi_list[j]['dt'];
                let end_type = bi_list[j]['vtype']
                let end_status = bi_list[j]['status'];

                console.log(start, end, start_type, end_type)

                let color = '#FFEB3B'
                let resolution = tvWidget.activeChart().resolution()
                if(resolution=="240"){
                  // color='#4CAF50'
                  color = '#FFEB3B'
                }else if(resolution=="30"){
                  color = '#FFEB3B'
                }else if(resolution=="5"){
                  color = '#FF9801'
                }else if(resolution=="1"){
                  color = '#F23545'
                }

                tvWidget.chart(0).createMultipointShape(
                [{time: Date.parse(start)/1000, channel: start_type},
                {time: Date.parse(end)/1000, channel: end_type},],
                {
                    shape: 'trend_line',
                    // lock: true,
                    // disableSelection: true,
                    // disableSave: true,
                    // disableUndo: true,
                    overrides: {
                        'linestyle': linestyle,
                        'linewidth': 1,
                        'linecolor': color,
                    }
                }
                );
              }
            });
        });
        btn_essence_xd.innerHTML = '<font color="#FFEB3B">本质线段</font>';

        // 参照线段（日线级别线段）
        const btn_consult_xd = tvWidget.createButton();
        btn_consult_xd.setAttribute('title', '日线线段');
        btn_consult_xd.classList.add('apply-common-tooltip');
        btn_consult_xd.addEventListener('click', function(){
          let sym = tvWidget.activeChart().symbol()
          let freq = tvWidget.activeChart().resolution()
          axios
            .get('http://127.0.0.1:8421/api/bzzs_mark?mtype=czxd_dg&tf='+freq+'&symbol='+sym)
            .then((res) => {
              console.log(';;;;;;;;get-avgkline-xd-list;;;;;;;;;;;;;');
              bi_list = res.data.data;
              // console.table(bi_list)

              let j = 0;
              for (var i = 0; i < bi_list.length-1; i++) {

                let start = bi_list[i]['dt'];
                let start_type = bi_list[i]['vtype']
                let start_status = bi_list[i]['is_valid_czxd'];

                j = i+1

                let end = bi_list[j]['dt'];
                let end_type = bi_list[j]['vtype']
                let end_status = bi_list[j]['is_valid_czxd'];

                console.log(start, end, start_type, end_type)

                let color = '#00FF7F'
                let linestyle = 0

                if(!end_status){
                  linestyle = 2;
                }

                tvWidget.chart(0).createMultipointShape(
                [{time: Date.parse(start)/1000, channel: start_type},
                {time: Date.parse(end)/1000, channel: end_type},],
                {
                    shape: 'trend_line',
                    // lock: true,
                    // disableSelection: true,
                    // disableSave: true,
                    // disableUndo: true,
                    overrides: {
                        'linestyle': linestyle,
                        'linewidth': 2,
                        'linecolor': color,
                    }
                }
                );

                // console.log(eid)
              }
            });
        });
        btn_consult_xd.innerHTML = '<font color="#00FF7F">日线线段</font>';        

        // 本质中枢
        const btn_bzzs = tvWidget.createButton();
        btn_bzzs.setAttribute('title', '本质中枢');
        btn_bzzs.classList.add('apply-common-tooltip');
        btn_bzzs.addEventListener('click', function(){
          let sym = tvWidget.activeChart().symbol()
          let freq = tvWidget.activeChart().resolution()
          axios
            .get('http://127.0.0.1:8421/api/bzzs_mark?mtype=bzzs&tf='+freq+'&symbol='+sym)
            .then((res) => {
              console.log(';;;;;;;;get-xdzs-list;;;;;;;;;;;;;');
              zs_list = res.data.data;
              console.table(zs_list);

              for (let item of zs_list) {
                var start_dt = item['start_dt']
                var end_dt = item['end_dt']
                var start_price = item['lower']
                var end_price = item['upper']

                // var is_nakedeye = item['is_nakedeye'];
                // let txt = item['zstext'];

                let trans = 85;
                let color = '#1E90FF';

                // if (is_nakedeye){
                //   color = '#00FF00'
                //   trans = 85;
                // }

                // tvWidget.chart(0).createShape(
                // {time: Date.parse(start_dt)/1000, price: end_price},
                //     {
                //     shape: 'text',
                //     lock: true,
                //     disableSelection: true,
                //     overrides: {
                //         'color': color,
                //         'text': txt,
                //         'fontsize': 15,
                //     }
                //   }
                // );

                tvWidget.chart(0).createMultipointShape(
                [{time: Date.parse(start_dt)/1000, price: start_price},
                {time: Date.parse(end_dt)/1000, price: end_price},],
                {
                    shape: 'rectangle',
                    // lock: true,
                    // disableSelection: true,
                    // disableSave: true,
                    // disableUndo: true,
                    zOrder: 'top',
                    overrides: {
                        'transparency': trans,
                        'linewidth': 1,
                        'color': color,
                        'backgroundColor': '#00FF00',
                    }
                }
                );
              }
            });
        });
        btn_bzzs.innerHTML = '<font color="#1E90FF">本质中枢</font>';

        // 三买点
        const btn_3buy = tvWidget.createButton();
        btn_3buy.setAttribute('title', '显示第三买卖点');
        btn_3buy.classList.add('apply-common-tooltip');
        btn_3buy.addEventListener('click', function(){
          let sym = tvWidget.activeChart().symbol()
          let freq = tvWidget.activeChart().resolution()
          axios
            .get('http://127.0.0.1:8421/api/bzzs_mark?mtype=3_buysell&tf='+freq+'&symbol='+sym)
            .then(function(res){
              console.log(';;;;;;;;get-zs-list;;;;;;;;;;;;;');
              zs_list = res.data.data;
                for (let item of zs_list) {
                  let buysell = item['3_buysell']
                  let dt = item['dt']

                  if(buysell=='buy'){
                    tvWidget.chart(0).createShape(
                    {
                        time: Date.parse(dt)/1000, channel: 'low'}, 
                        {
                        shape: 'arrow_up',
                        text: '3B',
                        overrides: {
                            'color': '#008000',
                            'size': 12,

                        }
                    }
                    );
                  }else if(buysell=='sell'){
                      tvWidget.chart(0).createShape(
                      {time: Date.parse(dt)/1000, channel: 'high'}, 
                          {
                          shape: 'arrow_down',
                          text: '3S',
                          overrides: {
                              'color': '#FF0000',
                              'size': 12,
                          }
                      }
                    );
                  }
                }
            });
        });
        btn_3buy.innerHTML = '三<font color="#008000">买</font><font color="#FF0000">卖</font>';        

        // 独立日线级别线段
        const btn_indp_cz = tvWidget.createButton();
        btn_indp_cz.setAttribute('title', '独立日线');
        btn_indp_cz.classList.add('apply-common-tooltip');
        btn_indp_cz.addEventListener('click', function(){
          let sym = tvWidget.activeChart().symbol()
          let freq = tvWidget.activeChart().resolution()
          axios
            .get('http://127.0.0.1:8421/api/bzzs_mark?mtype=indp_cz&tf='+freq+'&symbol='+sym)
            .then((resp) => {
              let bi_list = resp.data.data;
              console.log(';;;;;;;get-xd_xxk;;;;;;;')
              console.table(bi_list)
              for(var item of bi_list){
                let dt = item['dt']
                let vtype = item['vtype']
                let value = item['value']
                if(vtype =='high'){
                    tvWidget.chart(0).createShape(
                        {time: Date.parse(dt)/1000, price: value * 1.004}, 
                            {
                            shape: 'icon',
                            text: 'z',
                            overrides: {
                                'color': '#DC143C',
                                'icon': '0xf149',
                                'size': 25,
                            }
                        }
                    );
                }else if(vtype =='low'){
                  tvWidget.chart(0).createShape(
                        {time: Date.parse(dt)/1000, price: value * 0.996},
                            {
                            shape: 'icon',
                            text: 'z',
                            overrides: {
                                'color': '#DC143C',
                                'icon': '0xf148',
                                'size': 25,
                            }
                        }
                    ); 
                }
              }
            });
        });
        btn_indp_cz.innerHTML = '<font color="#DC143C">独立日线</font>';

        const button = tvWidget.createButton();
        button.setAttribute('title', 'Version');
        button.classList.add('apply-common-tooltip');
        button.addEventListener('click', () => tvWidget.showNoticeDialog({
            title: '联系作者',
            body: '<center>败火@自然之缠<br><br>Baihuo V1.0 2022.05.01 09:00<br><br> 微信：quantchan</center>',
            callback: () => {
              // eslint-disable-next-line no-console
              console.log('Baihuo V1.0 2022.05.01 09:00');
            },
          }));
        button.innerHTML = '联系作者';


        // 设置币种（不行）
        // const lnc_btn_selcoin = tvWidget.createButton();
        // lnc_btn_selcoin.setAttribute('title', '选币');
        // lnc_btn_selcoin.classList.add('apply-common-tooltip');
        // lnc_btn_selcoin.addEventListener('click', function(){
        //   widget.activeChart().setSymbol('ETH');
        // });
        // lnc_btn_selcoin.innerHTML = '<font color="#DC143C">选币</font>';

      });

      console.log("baihuo: chart_type", tvWidget.activeChart().chartType());

      // 改变可视范围时，可以执行定于
      // tvWidget.activeChart().onVisibleRangeChanged().subscribe(
      // null,
      // ({from, to }) => console.log(from, to)
      // );

      tvWidget.changeTheme('Dark');

      // 0: bar
      // 9: Hollow Candle
      tvWidget.activeChart().setChartType(9);

      // 设置上海的时区
      // 设置这个时区后，显示的数据，会相应的+8小时
      // tvWidget.activeChart().setTimezone("Asia/Shanghai");

      // tvWidget.activeChart().createStudy('NMA', false, false);  
      // tvWidget.activeChart().createStudy('MA34XD', false, false);  
      // tvWidget.activeChart().createStudy('NMM', false, false);

      
      // tvWidget.activeChart().createStudy('MACD',
      // false, false, [12, 26, "close", 9], 
      // {
      //   'Histogram.color': '#FF0000',
      //   'MACD.color': '#2962FF',
      //   'Signal.color': '#FF6D01',
      // });

      /*
      tvWidget.activeChart().createStudy('MACD',
      false, false, [16, 32, "close", 8], 
      {
        'Histogram.color': '#FF0000',
        'MACD.color': '#FFFFFF',
        'Signal.color': '#FFFF00',
        'Histogram.sxxtyle': 'Column',
      });

      tvWidget.activeChart().createStudy('MACD', 
      false, false, [32, 64, "close", 16], 
      {
        'Histogram.color': '#FF0000',
        'MACD.color': '#FFFFFF',
        'Signal.color': '#FFFF00',
      });
      */

      /*
      tvWidget.activeChart().createStudy('Moving Average Triple', 
      false, false, [4, 8, 16], 
      {
        'Plot 1.color': '#F8F8FF',
        'Plot 2.color': '#FFFF00',
        'Plot 3.color': '#800080'
      });
      tvWidget.activeChart().createStudy('Moving Average Triple', 
      false, false, [16, 32, 64], 
      {
        'Plot 1.color': '#800080',
        'Plot 2.color': '#0000FF',
        'Plot 3.color': '#008000'
      });
      */

      // tvWidget.activeChart().createStudy('Moving Average', 
      // false, false, [7], 
      // {
      //   'Plot.color': '#FFFFFF'
      // });

      // tvWidget.activeChart().createStudy('Moving Average', 
      // false, false, [34],
      // {
      //   'Plot.color': '#FF0000'
      // });

      // tvWidget.activeChart().createStudy('Moving Average',
      // false, false, [170],
      // {
      //   'Plot.color': '#00FF7F'
      // });

      // let sym = tvWidget.activeChart().symbol()
      // var prec = 2;
      // axios
      //       .get('http://127.0.0.1:8421/api/bzzs_mark?mtype=3_buysell&tf='+freq+'&symbol='+sym)
      //       .then(function(res){
      //         console.log(';;;;;;;;get-zs-list;;;;;;;;;;;;;');
      //         zs_list = res.data.data;
      // } 
           
      tvWidget.activeChart().createStudy('Moving Average Triple',
      false, false, [5, 34, 170],
      {
        'Plot 1.color': '#FFFFFF',
        'Plot 2.color': '#FF40FF',
        'Plot 3.color': '#0433FF',
        'precision': 2,
      });

      // 股票数据
      // tvWidget.activeChart().createStudy('Moving Average Triple',
      // false, false, [5, 34, 170],
      // {
      //   'Plot 1.color': '#FFFFFF',
      //   'Plot 2.color': '#FF40FF',
      //   'Plot 3.color': '#0433FF',
      //   'precision': 2,
      // });
      
      // tvWidget.activeChart().createStudy('Moving Average Triple',
      // false, false, [20, 24, 28],
      // {
      //   'Plot 1.color': '#25C6DA',
      //   'Plot 2.color': '#FBC02D',
      //   'Plot 3.color': '#673AB7',
      //   'precision': 2,
      // });

      // tvWidget.activeChart().createStudy('Moving Average Triple',
      // false, false, [36, 40, 44],
      // {
      //   'Plot 1.color': '#A937FF',
      //   'Plot 2.color': '#4CAF50',
      //   'Plot 3.color': '#03BFA5',
      //   'precision': 2,
      // });

      // tvWidget.activeChart().createStudy('Moving Average Triple',
      // false, false, [48, 52, 60],
      // {
      //   'Plot 1.color': '#F48FB1',
      //   'Plot 2.color': '#82B1FF',
      //   'Plot 3.color': '#FF5252',
      //   'precision': 2,
      // });
      // 

      /* tvWidget.activeChart().createStudy('Moving Average', 
      false, false, [8], 
      {
        'Plot.color': '#FFFF00'
      });
      tvWidget.activeChart().createStudy('Moving Average', 
      false, false, [16], 
      {
        'Plot.color': '#800080'
      });
      tvWidget.activeChart().createStudy('Moving Average', 
      false, false, [32], 
      {
        'Plot.color': '#0000FF'
      });
      tvWidget.activeChart().createStudy('Moving Average', 
      false, false, [64], 
      {
        'Plot.color': '#008000'
      }); */
   
      /*
      tvWidget.activeChart().createStudy('Bollinger Bands', 
      false, false,  [16, 1.382], 
      {
        'Median.color': '#0000FF',
        'Upper.color': '#DB7093',
        'Lower.color': '#DB7093',
      });

      tvWidget.activeChart().createStudy('Bollinger Bands', 
      false, false,  [16, 2], 
      {
        'Median.color': '#0000FF',
        'Upper.color': '#FF1493',
        'Lower.color': '#FF1493',
      });

      tvWidget.activeChart().createStudy('Bollinger Bands', 
      false, false,  [16, 2.764],
      {
        'Median.color': '#0000FF',
        'Upper.color': '#DC143C',
        'Lower.color': '#DC143C',
      });

      tvWidget.activeChart().createStudy('Bollinger Bands', 
      false, false,  [32, 1.382], 
      {
        'Median.color': '#0000FF',
        'Upper.color': '#DB7093',
        'Lower.color': '#DB7093',
      });

      tvWidget.activeChart().createStudy('Bollinger Bands', 
      false, false,  [32, 2], 
      {
        'Median.color': '#0000FF',
        'Upper.color': '#FF1493',
        'Lower.color': '#FF1493',
      });

      tvWidget.activeChart().createStudy('Bollinger Bands', 
      false, false,  [32, 2.764],
      {
        'Median.color': '#0000FF',
        'Upper.color': '#DC143C',
        'Lower.color': '#DC143C',
      });


      tvWidget.activeChart().createStudy('Bollinger Bands', 
      false, false,  [64, 1.382], 
      {
        'Median.color': '#0000FF',
        'Upper.color': '#DB7093',
        'Lower.color': '#DB7093',
      });

      tvWidget.activeChart().createStudy('Bollinger Bands', 
      false, false,  [64, 2], 
      {
        'Median.color': '#0000FF',
        'Upper.color': '#FF1493',
        'Lower.color': '#FF1493',
      });

      tvWidget.activeChart().createStudy('Bollinger Bands', 
      false, false,  [64, 2.764],
      {
        'Median.color': '#0000FF',
        'Upper.color': '#DC143C',
        'Lower.color': '#DC143C',
      });

      */

      // 主要的5个指标
      // // tvWidget.activeChart().createStudy('NMA', false, false);
      // tvWidget.activeChart().createStudy('NMC', false, false);
      // tvWidget.activeChart().createStudy('NMC2', false, false);
      // tvWidget.activeChart().createStudy('NXC', false, false);
      // // // tvWidget.activeChart().createStudy('NDX', false, false);
      // // // // tvWidget.activeChart().createStudy('NST', false, false);
      // tvWidget.activeChart().createStudy('NDX_NST', false, false);


      // tvWidget.activeChart().createStudy('MSH', false, false);.8998.9613-----
      // tvWidget.activeChart().createStudy('NMM', false, false);
      //tvWidget.activeChart().createStudy('bhbi', false, true);
      //tvWidget.activeChart().createStudy('newfx', false, true);
      // tvWidget.chart().createStudy('abcd crypto index', false, false);
      // tvWidget.chart().createStudy('Equity', false, true);
      // tvWidget.activeChart().createStudy('baihuoRSI', false, false);
      // tvWidget.getStudiesList().forEach(({ name }) => console.log('stuieds: ', name));

      // tvWidget.activeChart().dataReady(() => {
      // });
    // tvWidget.activeChart().createStudy('baihuo', true, false, [26], null, {checkLimit: false, priceScale: 'new-left'});
		});
  },

  destroyed() {
    if (this.tvWidget !== null) {
      this.tvWidget.remove();
      this.tvWidget = null;
    }
  }
}
</script>

<style lang="scss" scoped>
.ChanContainer {
  height: calc(100vh - 20px);
}
</style>
