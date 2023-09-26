$(document).ready(function(){
    $("div.open_pearsman").hide();
  });
  $(document).ready(function(){
    $("b.close1").hide();
  });
  $(document).ready(function(){
    $("span.click_it_1").click(function(){
      $("div.open_pearsman").toggle();
      $("b.open1").toggle();
      $("b.close1").toggle();
    });
  });
  $(document).ready(function(){
    $("div.open_table").hide();
  });
  $(document).ready(function(){
    $("b.close2").hide();
  });
  $(document).ready(function(){
    $("span.click_it_2").click(function(){
      $("div.open_table").toggle();
      $("b.open2").toggle();
      $("b.close2").toggle();
    });
  });
  $(document).ready(function(){
    $("div.open_pie").hide();
  });
  $(document).ready(function(){
    $("b.close3").hide();
  });
  $(document).ready(function(){
    $("span.click_it_3").click(function(){
      $("div.open_pie").toggle();
      $("b.open3").toggle();
      $("b.close3").toggle();
    });
  });
  $(document).ready(function(){
    $("div.df_head").hide();
  });
  $(document).ready(function(){
    $("b.close4").hide();
  });
  $(document).ready(function(){
    $("span.click_it_4").click(function(){
      $("div.df_head").toggle();
      $("b.open4").toggle();
      $("b.close4").toggle();
    });
  });
  //以下是為了顯示預覽處理後資料集的語法
function arrayToTable(tableData) {
var table = $('<center><table></table></center>');
$(tableData).each(function (i, rowData) {
    var row = $('<tr></tr>');
    $(rowData).each(function (j, cellData) {
        row.append($('<td>'+cellData+'</td>'));
    });
    table.append(row);
});
return table;
}

$.ajax({
    type: "GET",
    url: "/static/tmp/df_head.csv",
    success: function (data) {
        $('div.df_head').append(arrayToTable(Papa.parse(data).data));
    }
});