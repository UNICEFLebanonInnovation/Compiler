   var data = {
       2020: [
           ['Lebanese', 1256916],
           ['Syrians', 804000],
           ['PRL', 68580],
           ['PRS', 10138],
       ],
   };

   var countries = [{
       name: 'Lebanese',
       color: 'rgba(255, 152, 0,0.4)',
       borderColor:'#074650'
   }, {
       name: 'Syrians',
       color: 'rgba(0, 162, 255,0.4)',
       borderColor: '#009292'
   }, {
       name: 'PRL',
       color: 'rgba(163, 102, 188,0.4)',
       borderColor: '#FE6DB6'
   }, {
       name: 'PRS',
       color: 'rgba(158, 229, 161,0.4)',
       borderColor: '#FEB5DA'
   }];

   function getData(data) {
       return data.map(function (country, i) {
           return {
               name: country[0],
               y: country[1],
               color: countries[i].color,
               borderColor: countries[i].borderColor
           };
       });
   }

   function getRandomNumber(){
        return Math.floor((Math.random() * 100) + 1);
   }

   Highcharts.theme = {
           colors: ['#074650', '#009292', '#FE6DB6', '#FEB5DA', '#480091', '#B66DFF'],
           title: {
               style: {
                   color: '#4D4D4D',
                   fontFamily: '"Poppins"',
                   fontSize:'18px',
                   fontWeight:'300',
               }
           },
           subtitle: {
               style: {
                   color: '#6A707E',
                   fontFamily: '"Poppins"',
                   fontSize:'13px',
                   fontWeight:'100',
               }
           },
           yAxis: {
               labels: {
                       style: {
                           color: '#525252',
                           fontFamily: '"Poppins"',
                           fontSize:'12px',
                           fontWeight:'100',
                       }
                   }
           },
           xAxis: {
               labels: {
                       style: {
                           color: '#525252',
                           fontFamily: '"Poppins"',
                           fontSize:'12px',
                           fontWeight:'100',
                       }
                   },
           },
           legend: {
               itemStyle: {
                   fontFamily: '"Poppins"',
                   fontSize:'13px',
                   fontWeight:'100',
                   color: '#ABAFB3'
               },
               itemHoverStyle:{
                   color: 'gray'
               },
               itemMarginTop: 10,
           },
           tooltip:{
               style: {
                   color: '#ABAFB3',
                   fontFamily: '"Poppins"',
                   fontSize:'12px',
                   fontWeight:'400',
               }
           },
           drilldown: {
               activeAxisLabelStyle: {
                   color: '#525252',
                   textDecoration:'none',
                   fontWeight:'100',
               },
               activeDataLabelStyle: {
                   color: '#ABAFB3',
                   display:'none'
               }
           },
           credits: {
    enabled: false
},
       };

   Highcharts.setOptions(Highcharts.theme);

   var children_per_gender_data = [{
               name: 'Male',
               y: 344,
               color: '#01B8AA'
           }, {
               name: 'Female',
               y: 434,
               color: '#FD625E'
           }];
   var children_cash_support_data = [{
               name: 'Haddi',
               y: 123,
               color: '#F17925'
           }, {
               name: 'Education Cash assistance',
               y: 2345,
               color: '#004753'
           }, {
               name: 'UNHCR cash assistance',
               y: 565,
               color: '#CCAA14'
           },{
               name: 'WFP cash assistance',
               y: 245,
               color: '#4B4C4E'
           }];

   var children_per_status_data = [{
               name: 'Married',
               y: 123,
               color: '#73B761'
           }, {
               name: 'Engaged',
               y: 2345,
               color: '#4A588A'
           }, {
               name: 'Divorced',
               y: 5,
               color: '#ECC846'
           },{
               name: 'Widowed',
               y: 0,
               color: '#CD4C46'
           },{
               name: 'Single',
               y: 1345,
               color: '#71AFE2'
           }];

    var children_per_programme_data = [{
                           name: "CBECE",
                           y: 233,
                           drilldown: "",
                           color: '#B66DFF'
                       },
                       {
                           name: "BLN",
                           y: 234,
                           drilldown: "",
                           color: '#480091'
                       },
                       {
                           name: "RS",
                           y: 233,
                           drilldown: "",
                           color: '#FEB5DA'
                       },
                       {
                           name: "YBLN",
                           y: 343,
                           drilldown: "",
                           color: '#FE6DB6'
                       },
                       {
                           name: "PSS",
                           y: 545,
                           drilldown: "",
                           color: '#009292'
                       },
                       {
                           name: "Digital component",
                           y: 767,
                           drilldown: "",
                           color: '#074650'
                       }];
    var children_per_nationality_data = [
                   {
                       name: "Lebanese",
                       y: 3864296,
                       drilldown: "Lebanese",
                       color: '#DC5B57',
                       borderColor:'#DC5B57'
                   },
                   {
                       name: "Syrian",
                       y: 1500000,
                       drilldown: "Syrian",
                       color: '#F3C911',
                       borderColor: '#F3C911'
                   },
                   {
                       name: "PRL",
                       y: 180000,
                       drilldown: "PRL",
                       color: '#4C5D8A',
                       borderColor: '#4C5D8A'
                   },
                   {
                       name: "PRS",
                       y: 27700,
                       drilldown: "PRS",
                       color: '#4A8DDC',
                       borderColor: '#4A8DDC'
                   }
               ];
    var children_per_nationality_data_drilldown = [
               {
                   name: "Lebanese",
                   id: "Lebanese",
                   data: [
                       [
                           "Under 1 year",
                           72758
                       ],
                       [
                           "Under 2 years",
                           171937
                       ],
                       [
                           "Under 5 years",
                           499339
                       ],
                       [
                           "3-5 years",
                           357407
                       ],
                       [
                           "6-14 years",
                           1218975
                       ],
                       [
                           "6-11 years",
                           770825
                       ],
                       [
                           "15-18 years",
                           477349
                       ],
                       [
                           "3-18 years",
                           1973031
                       ],
                       [
                           "0-5 years",
                           639012
                       ],
                       [
                           "0-17 years",
                           2135887
                       ],
                       [
                           "12-14 years",
                           367448
                       ],
                       [
                           "12-17 years",
                           726045
                       ],
                       [
                           "15-17 years",
                           358193
                       ],
                       [
                           "10-14 years",
                           622504
                       ]
                   ]
               },
               {
                   name: "Syrian",
                   id: "Syrian",
                   data: [
                       [
                           "Under 1 year",
                           30255
                       ],
                       [
                           "Under 2 years",
                           84544
                       ],
                       [
                           "Under 5 years",
                           257412
                       ],
                       [
                           "3-5 years",
                           167743
                       ],
                       [
                           "6-14 years",
                           401348
                       ],
                       [
                           "6-11 years",
                           293300
                       ],
                       [
                           "15-18 years",
                           118569
                       ],
                       [
                           "3-18 years",
                           687661
                       ],
                       [
                           "0-5 years",
                           312116
                       ],
                       [
                           "0-17 years",
                           805199
                       ],
                       [
                           "12-14 years",
                           108047
                       ],
                       [
                           "12-17 years",
                           199779
                       ],
                       [
                           "15-17 years",
                           91732
                       ],
                       [
                           "10-14 years",
                           197362
                       ]
                   ]
               },
               {
                   name: "PRL",
                   id: "PRL",
                   data: [
                       [
                           "Under 1 year",
                           3240
                       ],
                       [
                           "Under 2 years",
                           6689
                       ],
                       [
                           "Under 5 years",
                           17386
                       ],
                       [
                           "3-5 years",
                           10768
                       ],
                       [
                           "6-14 years",
                           30824
                       ],
                       [
                           "6-11 years",
                           20578
                       ],
                       [
                           "15-18 years",
                           14231
                       ],
                       [
                           "3-18 years",
                           55824
                       ],
                       [
                           "0-5 years",
                           21041
                       ],
                       [
                           "0-17 years",
                           62601
                       ],
                       [
                           "12-14 years",
                           10247
                       ],
                       [
                           "12-17 years",
                           20982
                       ],
                       [
                           "15-17 years",
                           10736
                       ],
                       [
                           "10-14 years",
                           16772
                       ]
                   ]
               },
               {
                   name: "PRS",
                   id: "PRS",
                   data: [
                       [
                           "Under 1 year",
                           527
                       ],
                       [
                           "Under 2 years",
                           1214
                       ],
                       [
                           "Under 5 years",
                           3017
                       ],
                       [
                           "3-5 years",
                           1758
                       ],
                       [
                           "6-14 years",
                           6022
                       ],
                       [
                           "6-11 years",
                           4216
                       ],
                       [
                           "15-18 years",
                           1973
                       ],
                       [
                           "3-18 years",
                           9753
                       ],
                       [
                           "0-5 years",
                           3631
                       ],
                       [
                           "0-17 years",
                           11172
                       ],
                       [
                           "12-14 years",
                           1806
                       ],
                       [
                           "12-17 years",
                           3325
                       ],
                       [
                           "15-17 years",
                           1518
                       ],
                       [
                           "10-14 years",
                           3252
                       ]
                   ]
               }
           ];
    var children_per_source_data = [{
                       name: "Dirassa",
                       y: 233,
                       drilldown: "",
                       color: '#01B8AA'
                   },
                   {
                       name: "Awareness Session",
                       y: 234,
                       drilldown: "",
                       color: '#374649'
                   },
                   {
                       name: "Sector Partners referral",
                       y: 233,
                       drilldown: "",
                       color: '#FD625E'
                   },
                   {
                       name: "From Profiling Database",
                       y: 343,
                       drilldown: "",
                       color: '#F2C80F'
                   },
                   {
                       name: "From Other NGO",
                       y: 545,
                       drilldown: "",
                       color: '#5F6B6D'
                   },
                   {
                       name: "From Displaced Community",
                       y: 767,
                       drilldown: "",
                       color: '#8AD4EB'
                   },
                   {
                       name: "Referred by the municipality",
                       y: 767,
                       drilldown: "",
                       color: '#FE9666'
                   },
                   {
                       name: "Other Sources",
                       y: 767,
                       drilldown: "",
                       color: '#A66999'
                   }];

   var children_per_gender = create_pie_chart('children_per_gender', 'Gender', children_per_gender_data);
   var children_cash_support = create_pie_chart('children_cash_support', 'Support type', children_cash_support_data);
   var children_per_status = create_pie_chart('children_per_status', 'Support type', children_per_status_data);

   var children_per_programme = create_bar_chart('children_per_programme', children_per_programme_data, [])
   var children_per_nationality = create_bar_chart('children_per_nationality', children_per_nationality_data, children_per_nationality_data_drilldown)
   var children_per_source = create_bar_chart('children_per_source', children_per_source_data, [])

   function create_pie_chart(container, series_name, data) {

       return Highcharts.chart(container, {
           chart: {
               plotBackgroundColor: null,
               plotBorderWidth: 0,
               plotShadow: false,
               type: 'pie'
           },
           title: {
               text: '',
               align: 'center',
               verticalAlign: 'middle',
               y: 50
           },
           subtitle: {
               text: '',
               align: 'left',
               verticalAlign: 'bottom',
           },
           tooltip: {
               pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
           },
           accessibility: {
               point: {
                   valueSuffix: '%'
               }
           },
           plotOptions: {
               pie: {
                   allowPointSelect: true,
                   cursor: 'pointer',
                   dataLabels: {
                       enabled: false,
                       format: '<b>{point.name}</b>: {point.percentage:.1f} %'
                   },
                   showInLegend: true
               }
           },
           legend: {
               align: 'right',
               verticalAlign: 'middle',
               layout: 'vertical',

           },
           series: [{
               name: series_name,
               colorByPoint: true,
               innerSize: '50%',
               data: data
           }]
       });
    }

   function create_bar_chart(container, data, drilldown) {

       return Highcharts.chart(container, {
           chart: {
               type: 'column',
                 margin:80,
               marginBottom:100,

           },
           title: {
               text: '',

           },
           subtitle: {
               text: '',
               align: 'left',
               verticalAlign: 'bottom',
           },
           accessibility: {
               announceNewData: {
                   enabled: true
               }
           },
           xAxis: {
               type: 'category'
           },
           yAxis: {
               title: {
                   text:' '
               }

           },
           legend: {
               enabled: false
           },
           plotOptions: {
               series: {
                   borderWidth: 1,
                   borderColor:'{point.borderColor}',
                   pointWidth:40,
                   dataLabels: {
                       enabled: false,
                       formatter: function() {
                         return formatNumber(this.point.y);
                       }
                   }
               }
           },

           tooltip: {
               formatter: function() {
                     return '<b>'+this.point.name+': </b>'+ formatNumber(this.point.y);
               }
           },

           series: [
               {
                   name: "",
                   colorByPoint: true,
                   data: data,
               }
           ],
           drilldown: {
               series: drilldown
           }
       });
   }


$(document).on('click',  '.filter-package-type', function(){

    $('.filter-package-type').removeClass('bg-light');
    $(this).addClass('bg-light');

    children_per_gender.update({
       series: [{
           data: generate_new_data(children_per_gender_data)
       }]
    });

    children_cash_support.update({
       series: [{
           data: generate_new_data(children_cash_support_data)
       }]
    });

    children_per_status.update({
       series: [{
           data: generate_new_data(children_per_status_data)
       }]
    });

    children_per_programme.update({
       series: [{
           data: generate_new_data(children_per_programme_data)
       }]
    });

    children_per_nationality.update({
       series: [{
           data: generate_new_data(children_per_nationality_data)
       }]
    });

    children_per_source.update({
       series: [{
           data: generate_new_data(children_per_source_data)
       }]
    });

});


function generate_new_data(data){

    var new_data = []

    $(data).each(function(i, item){
        item['y'] = getRandomNumber();
        new_data[i] = item
    });

    return new_data;
}
