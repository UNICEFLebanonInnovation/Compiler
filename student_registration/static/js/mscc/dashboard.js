   var data = {};

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

   var children_per_gender_data = [];
   var children_cash_support_data = [];
   var children_per_status_data = [];
   var children_per_programme_data = [];
   var children_per_nationality_data = [];
   var children_per_nationality_data_drilldown = [];
   var children_per_source_data = [];
   var children_per_disability_data = [];
   var children_per_vulnerability_data = [];
   var children_volunteering_data = [];

   var children_per_gender;
   var children_cash_support;
   var children_per_status;
   var children_per_programme;
   var children_per_nationality;
   var children_per_source;
   var children_per_disability;
   var children_per_vulnerability;
   var children_volunteering;

   function initDashboardCharts(dataset){
       children_per_gender_data = dataset.children_per_gender || [];
       children_cash_support_data = dataset.children_cash_support || [];
       children_per_status_data = dataset.children_per_status || [];
       children_per_programme_data = dataset.children_per_programme || [];
       children_per_nationality_data = dataset.children_per_nationality || [];
       children_per_source_data = dataset.children_per_source || [];
       children_per_disability_data = dataset.children_per_disability || [];
       children_per_vulnerability_data = dataset.children_per_vulnerability || [];
       children_volunteering_data = dataset.children_volunteering || [];

       children_per_gender = create_pie_chart('children_per_gender', 'Gender', children_per_gender_data);
       children_cash_support = create_pie_chart('children_cash_support', 'Support type', children_cash_support_data);
       children_per_status = create_pie_chart('children_per_status', 'Support type', children_per_status_data);

       children_per_programme = create_bar_chart('children_per_programme', children_per_programme_data, [])
       children_per_nationality = create_bar_chart('children_per_nationality', children_per_nationality_data, [])
       children_per_source = create_bar_chart('children_per_source', children_per_source_data, [])
       children_per_disability = create_pie_chart('children_per_disability', 'Disability', children_per_disability_data)
       children_per_vulnerability = create_bar_chart('children_per_vulnerability', children_per_vulnerability_data, [])
       children_volunteering = create_bar_chart('children_volunteering', children_volunteering_data, [])
   }

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
               },
                series: {
                    point: {
                        events: {
                            click: function () {
                                reload_dashboard_data(container);
                            }
                        }
                    }
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
                   },
                    point: {
                        events: {
                            click: function () {
                                reload_dashboard_data(container);
                            }
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

    reload_dashboard_data();
});

function reload_dashboard_data(exclude_container){
    $.getJSON('/mscc/dashboard-data/', function(resp){
        if(exclude_container != 'children_per_gender') {
            children_per_gender.update({
               series: [{ data: resp.children_per_gender }]
            });
        }

        if(exclude_container != 'children_cash_support') {
            children_cash_support.update({
               series: [{ data: resp.children_cash_support }]
            });
        }

        if(exclude_container != 'children_per_status') {
            children_per_status.update({
               series: [{ data: resp.children_per_status }]
            });
        }

        if(exclude_container != 'children_per_programme') {
            children_per_programme.update({
               series: [{ data: resp.children_per_programme }]
            });
        }

        if(exclude_container != 'children_per_nationality') {
            children_per_nationality.update({
               series: [{ data: resp.children_per_nationality }]
            });
        }

        if(exclude_container != 'children_per_source') {
            children_per_source.update({
               series: [{ data: resp.children_per_source }]
            });
        }

        if(exclude_container != 'children_per_disability') {
            children_per_disability.update({
               series: [{ data: resp.children_per_disability }]
            });
        }

        if(exclude_container != 'children_per_vulnerability') {
            children_per_vulnerability.update({
               series: [{ data: resp.children_per_vulnerability }]
            });
        }

        if(exclude_container != 'children_volunteering') {
            children_volunteering.update({
               series: [{ data: resp.children_volunteering }]
            });
        }

        children_per_gender_data = resp.children_per_gender;
        children_cash_support_data = resp.children_cash_support;
        children_per_status_data = resp.children_per_status;
        children_per_programme_data = resp.children_per_programme;
        children_per_nationality_data = resp.children_per_nationality;
        children_per_source_data = resp.children_per_source;
        children_per_disability_data = resp.children_per_disability;
        children_per_vulnerability_data = resp.children_per_vulnerability;
        children_volunteering_data = resp.children_volunteering;
    });
}

function generate_new_data(data){

    var new_data = []

    $(data).each(function(i, item){
        item['y'] = getRandomNumber();
        new_data[i] = item
    });

    return new_data;
}


function getPointCategoryName(point, dimension) {
    var series = point.series,
        isY = dimension === 'y',
        axis = series[isY ? 'yAxis' : 'xAxis'];
    return axis.categories[point[isY ? 'y' : 'x']];
}
