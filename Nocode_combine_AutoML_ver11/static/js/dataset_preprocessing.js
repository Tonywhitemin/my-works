
$(document).ready(function(){
    $("div.reset").hide();
  });
  
$(document).ready(function(){
$("span.button_inner").click(function(){
    $("div.reset").show();
});
});
/*221024新增類別特徵的動態處理*/

/*以下這段是將線況"有序"欄位的資訊以表格呈現並讓使用者定義代碼*/
$(document).ready(function(){
  $("div.ordinal_table_code_define").hide();
  $("span.self_or_default").hide();
});

$(document).ready(function(){
  $("input.ordinal_dont_expand").click(function(){
    $("div.ordinal_table_code_define").hide();
    $("span.self_or_default").hide();
  });
});

$(document).ready(function(){
  $("input.ordinal_expand").click(function(){
    $("span.self_or_default").show();
  });
});



$(document).ready(function(){
  $("input.self_define_ordinal").click(function(){
    $("div.ordinal_table_code_define").show();
  });
});

$(document).ready(function(){
  $("input.follow_default_ordinal").click(function(){
    $("div.ordinal_table_code_define").hide();
  });
});

/*221101新增判定若使用者要直接刪除缺失欄位則補值選項先隱藏*/
$(document).ready(function(){
  $("div.based_on_dropna_or_not").hide();

});
/*以下為若使用者刪除缺失欄位時填補欄位要隱藏*/
$(document).ready(function(){
  $("input.drop_yes").click(function(){
    $("div.click_then_hide").hide();
    $("div.based_on_dropna_or_not").show();
    $("div.if_drop_then_hide").hide();
    $("div.not_drop").hide();
  });
});

$(document).ready(function(){
  $("input.drop_no").click(function(){
    $("div.click_then_hide").hide();
    $("div.based_on_dropna_or_not").show();
    $("div.if_drop_then_hide").show();
  });
});

$(document).ready(function(){
  $("input.if_choosed_then_show").click(function(){
    $("div.not_drop").show();
  });
});

$(document).ready(function(){
  $("input.if_choosed_then_hide").click(function(){
    $("div.not_drop").hide();
  });
});
/*221102針對一開始就沒有缺失值（dataset_preprocessing.html）特別增加的指令*/
$(document).ready(function(){
  $("div.if_outlier_yes_then_show").hide();
});

$(document).ready(function(){
  $("input.if_choosed_then_show").click(function(){
    $("div.if_outlier_yes_then_show").show();
  });
});

$(document).ready(function(){
  $("input.if_choosed_then_hide").click(function(){
    $("div.if_outlier_yes_then_show").hide();
  });
});

//221108改成依欄位處理,以下為三個按鈕按下去分別展開不同屬性欄位的表格
$(document).ready(function(){
  $("div.numerical_check").hide();
  $("div.ordinal_check").hide();
  $("div.nominal_check").hide();
  $("label.numerical_table_closed").hide();
  $("label.ordinal_table_closed").hide();
  $("label.nominal_table_closed").hide();
});
//數值型展開收合
$(document).ready(function(){
  $("label.numerical").click(function(){
    $("div.numerical_check").show();
    $("label.numerical_table_closed").show();
    $("label.numerical").hide();
    $("div.ordinal_check").hide();
    $("div.nominal_check").hide();
    $("div.ordinal_table_code_define").hide();
  });
});

$(document).ready(function(){
  $("label.numerical_table_closed").click(function(){
    $("div.numerical_check").hide();
    $("label.numerical_table_closed").hide();
    $("label.numerical").show();
  });
});
//有序型展開收合
$(document).ready(function(){
  $("label.ordinal").click(function(){
    $("div.ordinal_check").show();
    $("label.ordinal_table_closed").show();
    $("label.ordinal").hide();
    $("div.numerical_check").hide();
    $("div.nominal_check").hide();
  });
});
$(document).ready(function(){
  $("label.ordinal_table_closed").click(function(){
    $("div.ordinal_check").hide();
    $("label.ordinal_table_closed").hide();
    $("label.ordinal").show();
    $("div.ordinal_table_code_define").hide();
  });
});


//無序型展開收合
$(document).ready(function(){
  $("label.nominal").click(function(){
    $("div.nominal_check").show();
    $("label.nominal_table_closed").show();
    $("label.nominal").hide();
    $("div.numerical_check").hide();
    $("div.ordinal_check").hide();
    $("div.ordinal_table_code_define").hide();
  });
});
$(document).ready(function(){
  $("label.nominal_table_closed").click(function(){
    $("div.nominal_check").hide();
    $("label.nominal_table_closed").hide();
    $("label.nominal").show();
  });
});

//221108若有序類別變數使用者自定義label encoding時要顯示的欄位
//以下這段參考:https://social.msdn.microsoft.com/Forums/zh-TW/2030bd82-3acd-4a41-bb5c-eb388f03c0a8/select-1997925289243353698421934?forum=236
$(function(){
  //全部選擇隱藏
  $('div[id^="tab_"]').hide();
  $("select.ordinal_translate").change(function(){
    let sltValue=$(this).val();
    console.log(sltValue);
    
    $('div[id^="tab_"]').hide();
    //指定選擇顯示
    $(sltValue).show();
  });
});


//221201修正bug for如果使用者點選其他表格展開時要把自定義那個表格收起來
$(document).ready(function(){
  $("label.nominal").click(function(){
    $("div#tab_1").hide();
  });
  $("label.nominal_table_closed").click(function(){
    $("div#tab_1").hide();
  });
  $("label.numerical").click(function(){
    $("div#tab_1").hide();
  });
  $("label.numerical_table_closed").click(function(){
    $("div#tab_1").hide();
  });
  $("label.ordinal_table_closed").click(function(){
    $("div#tab_1").hide();
  });
});

//221109測試若點選刪除欄位dropna則其餘選項disable
//221115以下為數值型表格對應disable功能
$(document).ready(function(){
  $("select[id^='numericalid']").change(function(){ //此行正則表示法是取出所有id為numericalid開頭的所有標籤
    console.log(this.id); //輸出該id值到前端console確認
    var numericalid_to_disable=this.id //將該id轉為字串
    var numerical_disableid='#numerical_disableid'+numericalid_to_disable.substr(11) //定義一個變數對應從numericalid到'#numerical_disableid
    console.log(numerical_disableid); //確認結果
    $(numerical_disableid).prop('disabled',(i, v) => !v); //利用對應變數執行disable動作，//221110 (i, v) => !v這個用法等同於toggle，在使用者若從是改為否時會取消反灰底，參考網址:https://stackoverflow.com/questions/4702000/toggle-input-disabled-attribute-using-jquery
  });
});
//221115以下為有序類別型表格對應disable功能
$(document).ready(function(){
  $("select[id^='ordinalid']").change(function(){ //此行正則表示法是取出所有id為ordinalid開頭的所有標籤
    console.log(this.id); //輸出該id值到前端console確認
    var ordinalid_to_disable=this.id //將該id轉為字串
    var ordinalid_disableid='#ordinal_disableid'+ordinalid_to_disable.substr(9) //定義一個變數對應從ordinalid到'#ordinalid_disableid
    console.log(ordinalid_disableid); //確認結果
    $(ordinalid_disableid).prop('disabled',(i, v) => !v); //利用對應變數執行disable動作，//221110 (i, v) => !v這個用法等同於toggle，在使用者若從是改為否時會取消反灰底，參考網址:https://stackoverflow.com/questions/4702000/toggle-input-disabled-attribute-using-jquery
  });
});

//221115以下為無序類別型表格對應disable功能
$(document).ready(function(){
  $("select[id^='nominalid']").change(function(){ //此行正則表示法是取出所有id為nominalid開頭的所有標籤
    console.log(this.id); //輸出該id值到前端console確認
    var nominalid_to_disable=this.id //將該id轉為字串
    var nominalid_disableid='#nominal_disableid'+nominalid_to_disable.substr(9) //定義一個變數對應從nominalid到'#nominalid_disableid
    console.log(nominalid_disableid); //確認結果
    $(nominalid_disableid).prop('disabled',(i, v) => !v); //利用對應變數執行disable動作，//221110 (i, v) => !v這個用法等同於toggle，在使用者若從是改為否時會取消反灰底，參考網址:https://stackoverflow.com/questions/4702000/toggle-input-disabled-attribute-using-jquery
  });
});
//＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝


//221115測試當欄位被使用者指定刪除時後面選項要disable
//以下為數值型
$(document).ready(function(){
  $("select[id^='numerical_drop_col_disable_']").change(function(){ 
    var sourceID=this.id 
    var outlier_disable='.disable_outlier_'+sourceID.substr(27)
    var normalization_disable='.disable_normalization_'+sourceID.substr(27)
    var dropna_disable='#numericalid'+sourceID.substr(27)
    var fillna_disable='#numerical_disableid'+sourceID.substr(27)
    $(outlier_disable).prop('disabled',(i, v) => !v);
    $(fillna_disable).prop('disabled',(i, v) => !v);
    $(dropna_disable).prop('disabled',(i, v) => !v);
    $(normalization_disable).prop('disabled',(i, v) => !v);
    
  });
});

//以下為有序類別型
$(document).ready(function(){
  $("select[id^='ordinal_drop_col_disable_']").change(function(){ 
    var ord_sourceID=this.id 
    var ord_dropna_disable='#ordinalid'+ord_sourceID.substr(25)
    var ord_fillna_disable='#ordinal_disableid'+ord_sourceID.substr(25)
    var ord_handle_disable='#ord_handle_'+ord_sourceID.substr(25)
    
    $(ord_fillna_disable).prop('disabled',(i, v) => !v);
    $(ord_dropna_disable).prop('disabled',(i, v) => !v);
    $(ord_handle_disable).prop('disabled',(i, v) => !v);

  });
});
//以下為無序類別型
$(document).ready(function(){
  $("select[id^='nominal_drop_col_disable_']").change(function(){ 
    var nom_sourceID=this.id 
    var nom_dropna_disable='#nominalid'+nom_sourceID.substr(25)
    var nom_fillna_disable='#nominal_disableid'+nom_sourceID.substr(25)

    $(nom_fillna_disable).prop('disabled',(i, v) => !v);
    $(nom_dropna_disable).prop('disabled',(i, v) => !v);

  });
});
