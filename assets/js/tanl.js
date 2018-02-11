<script src="/assets/bower_components/jquery/dist/jquery.min.js"></script>


<script type="text/javascript">
$.ready(function(){
  $(".dropdown-content").each(function(){
      $(this).removeClass("show");
    })
})
  function searchChange(ctl){
    search_text = $(ctl).val();
    $.ajax({
        url: '/search/' + search_text,
        error: function() {
            //$('#searchNotification').html('<p>An error has occurred</p>');
            $(".dropdown-content").each(function(){
              $(this).removeClass("show");
            })
        },
        dataType: 'json',
        success: function(data) {
            build_table_results(data);
        },
        type: 'GET'
      });
  }
  function option_click(ctl){
    $('#myDropdown').removeClass("show");
    $("#searchBox").val($(ctl).html())
    searchResults($(ctl).html());
  }

  function build_table_results(rows){
    temp_html = ""

    $.each(rows, function(index,row){
      temp_html = temp_html + '<a href="#" onclick="option_click(this);">' + row + '</a>'
    });

    $("#myDropdown").html(temp_html);
    $('#myDropdown').addClass("show");
    //$(".dropdown-content").each(function(){
    //  $(this).addClass("show");
    //})
  }

  function searchResults(search_text){
    //search_text = $('searchBox').val();
    $.ajax({
        url: '/searchresults/' + search_text,
        error: function() {
            //$('#searchNotification').html('<p>An error has occurred</p>');
            $('#searchNotification').html("");
        },
        dataType: 'json',
        success: function(data) {
          console.log(data);

          temp_html = '<div class="" style="float:left">' +
            '<h4 style="text-align:center"></h4>' +
            '<div id="chart" class="chart-container">' +
            '</div>' +
            '</div>"'
          temp_html = ""
          group = data.data
          console.log(data)
          temp1_html = '<div id="lineContainer" class="chartCont" style="display:inline-block;width:100%;" >' +
                                  '<div id="chart_line" class="chart-container1">' +
                                  '</div>' +
                              '</div>' +
                              '<div id="barContainer" class="chartCont" style="display:inline-block;width:100%" >' +
                                  '<div id="chart_bar" class="chart-container1">' +
                                  '</div>' +
                              '</div>' +
                              '<div id="areaContainer" class="chartCont" style="display:inline-block;width:100%" >' +
                                  '<div id="chart_area" class="chart-container1">' +
                                  '</div>' +
                              '</div>' +
                              '<div id="stackedContainer" class="chartCont" style="display:inline-block;width:100%" >' +
                                  '<div id="chart_stacked" class="chart-container1">' +
                                  '</div>' +
                                '</div>'

          for(i=0;i<group.length;i++){
                temp_html = temp_html + '<div class="" style="display:inline-block">' +
                                '<div id="chart-' + group[i]["group"].replace(" ","-") + '" class="chart-container">' +
                                '</div>' +
                                '<span style="text-align:center;font-style:bold">' + group[i]["group"] + '</span>' +
                              '</div>'
              }
              $('#searchNotification').html("");
              $('#searchNotification').html('<div id="pieContainer" class="chartCont" style="display:inline-block">' + temp_html + '</div>' + temp1_html);

                for(i=0;i<group.length;i++){
                  //piechart(group[i]["result"], 'chart-' + group[i]["group"].replace(" ","-"));
                  Morris.Donut({
                    element: 'chart-' + group[i]["group"].replace(" ","-"),
                    data: group[i]["result"],
                      formatter: function (x) { return x + "%"}
                    });
                }



              config = {
                  data: data.data,
                    xkey: data.x_key,
                    ykeys: data.y_keys,
                    labels: data.y_labels,
                    hideHover: 'auto',
                    lineColors: data.colors,
                    barColors: data.colors
                };
                config.element = "chart_line"
                Morris.Line(config)
                config.element = "chart_area"
                Morris.Area(config)
                config.element = "chart_bar"
                Morris.Bar(config)
                config.stacked = true;
                config.element = "chart_stacked"
                Morris.Bar(config)
                selectChart(data["chartType"])

        },
        type: 'GET'
      });
  }


function selectChart(type){
  $('.chartoption').each(function(){
    $(this).removeClass('selectedChart');
  })

  $('.chartCont').each(function(){
    $(this).addClass('hide');
  })
  $('#' + type + 'Chart').addClass('selectedChart')
  $('#' + type + 'Container').removeClass('hide')

}

function piechart(dataset, elementName){
    var pie=d3.layout.pie()
            .value(function(d){return d.percent})
            .sort(null)
            .padAngle(.03);

    var w=200,h=200;

    var outerRadius=w/2;
    var innerRadius=65;

    var color = d3.scale.category10();

    var arc=d3.svg.arc()
            .outerRadius(outerRadius)
            .innerRadius(innerRadius);

    var svg=d3.select("#" + elementName)
            .append("svg")
            .attr({
                width:w,
                height:h,
                class:'shadow'
            }).append('g')
            .attr({
                transform:'translate('+w/2+','+h/2+')'
            });
    var path=svg.selectAll('path')
            .data(pie(dataset))
            .enter()
            .append('path')
            .attr({
                d:arc,
                fill:function(d,i){
                    return color(d.data.name);
                }
            });

    path.transition()
            .duration(1000)
            .attrTween('d', function(d) {
                var interpolate = d3.interpolate({startAngle: 0, endAngle: 0}, d);
                return function(t) {
                    return arc(interpolate(t));
                };
            });


    var restOfTheData=function(){
        var text=svg.selectAll('text')
                .data(pie(dataset))
                .enter()
                .append("text")
                .transition()
                .duration(200)
                .attr("transform", function (d) {
                    return "translate(" + arc.centroid(d) + ")";
                })
                .attr("dy", ".4em")
                .attr("text-anchor", "middle")
                .text(function(d){
                    return d.data.percent+"%";
                })
                .style({
                    fill:'#fff',
                    'font-size':'10px'
                });

        var legendRectSize=20;
        var legendSpacing=7;
        var legendHeight=legendRectSize+legendSpacing;


        var legend=svg.selectAll('.legend')
                .data(color.domain())
                .enter()
                .append('g')
                .attr({
                    class:'legend',
                    transform:function(d,i){
                        //Just a calculation for x & y position
                        return 'translate(-35,' + ((i*legendHeight)-65) + ')';
                    }
                });
        legend.append('rect')
                .attr({
                    width:legendRectSize,
                    height:legendRectSize,
                    rx:20,
                    ry:20
                })
                .style({
                    fill:color,
                    stroke:color
                });

        legend.append('text')
                .attr({
                    x:30,
                    y:35
                })
                .text(function(d){
                    return d;
                }).style({
                    fill:'#929DAF',
                    'font-size':'12px'
                });
    };

    setTimeout(restOfTheData,1000);
  }
</script>