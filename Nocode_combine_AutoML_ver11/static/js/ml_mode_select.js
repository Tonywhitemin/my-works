
 //====第零段：使用者點擊非監督式學習，其他欄位都要收起來====
 $(document).ready(function(){
    $("label.unsuper").click(function(){
      $("form.unsuper").show();
      $("div.super_mission_type").hide();
      $("div.super_regression_eva").hide();
      $("div.binary_class_eva").hide();
      $("div.multi_class_eva").hide();
      $("div.mode_select").hide();
      $("div.algorithms").hide();
      $("div.ensemble_stacking").hide();
      $("div.validation_strategy").hide();
      $("div.vali_split").hide();
      $("div.vali_k_folds").hide();
      $("div.Golden_Features").hide();
      $("div.features_selection").hide();
      $("div.start_random_models").hide();
      $("div.hill_climbing_steps").hide();
      $("button.button").hide();
      $("div.self_define").hide();
      $("img.super").hide();
      $("img.unsuper").hide();
      $("img.unsuper2").show();
  });
  })
  //
//====第一段：一開始讓使用者選擇監督非監督以外剩餘功能都藏起來====
$(document).ready(function(){
    $("div.super_mission_type").hide();
    $("div.super_regression_eva").hide();
    $("div.binary_class_eva").hide();
    $("div.multi_class_eva").hide();
    $("div.mode_select").hide();
    $("div.algorithms").hide();
    $("div.ensemble_stacking").hide();
    $("div.validation_strategy").hide();
    $("div.vali_split").hide();
    $("div.vali_k_folds").hide();
    $("div.Golden_Features").hide();
    $("div.features_selection").hide();
    $("div.start_random_models").hide();
    $("div.hill_climbing_steps").hide();
    $("form.unsuper").hide();
    $("button.button").hide();
    $("div.self_define").hide();
    $("img.unsuper2").hide();
});
//====第一段結束=====
//====第二段：使用者點擊監督式學習====
$(document).ready(function(){
$("label.super").click(function(){
    $("div.super_mission_type").show();//任務型態先顯示出來
    $("div.super_regression_eva").show();//因為預設為回歸，故回歸的評價指標一起出來
    $("div.mode_select").show();//模式選擇也可先顯示出來
    $("button.button").show();//因為預設是簡易模式，可讓送出按鈕出現
    $("form.unsuper").hide();
    $("img.unsuper").hide();
    $("img.super").hide();
});
})
//當使用者任務點回歸
$(document).ready(function(){
$("input.regression").click(function(){
    $("div.super_regression_eva").show();
    $("div.binary_class_eva").hide();
    $("div.multi_class_eva").hide();
});
})
//當使用者任務點二元分類
$(document).ready(function(){
$("input.binary").click(function(){
    $("div.super_regression_eva").hide();
    $("div.binary_class_eva").show();
    $("div.multi_class_eva").hide();
});
})
//當使用者任務點多元分類
$(document).ready(function(){
$("input.multi").click(function(){
    $("div.super_regression_eva").hide();
    $("div.binary_class_eva").hide();
    $("div.multi_class_eva").show();
});
})
//====第二段結束=====
//====第三段：使用者點擊自定義模式====
$(document).ready(function(){
$("label.compete").click(function(){
    $("div.algorithms").show();
    $("div.ensemble_stacking").show();
    $("div.validation_strategy").show();
    $("div.vali_split").show();//預設是split mode所以這裡要顯示出來
    $("div.Golden_Features").show();
    $("div.features_selection").show();
    $("div.start_random_models").show();
    $("div.hill_climbing_steps").show();
    $("div.self_define").show();
    });
})
//當使用者又點回快速模式時要收回
$(document).ready(function(){
$("label.explain").click(function(){
    $("div.algorithms").hide();
    $("div.ensemble_stacking").hide();
    $("div.validation_strategy").hide();
    $("div.vali_split").hide();
    $("div.vali_k_folds").hide();
    $("div.Golden_Features").hide();
    $("div.features_selection").hide();
    $("div.start_random_models").hide();
    $("div.hill_climbing_steps").hide();
    $("div.self_define").hide();
});
})
//當使用者點擊驗證模式時要做相對切換
$(document).ready(function(){
    $("input.split").click(function(){
    $("div.vali_split").show();
    $("div.vali_k_folds").hide();
    });
})
$(document).ready(function(){
    $("input.kfold").click(function(){
    $("div.vali_split").hide();
    $("div.vali_k_folds").show();
});
})
//====第三段結束===== //====第零段：使用者點擊非監督式學習，其他欄位都要收起來====
$(document).ready(function(){
$("label.unsuper").click(function(){
    $("form.unsuper").show();
    $("div.super_mission_type").hide();
    $("div.super_regression_eva").hide();
    $("div.binary_class_eva").hide();
    $("div.multi_class_eva").hide();
    $("div.mode_select").hide();
    $("div.algorithms").hide();
    $("div.ensemble_stacking").hide();
    $("div.validation_strategy").hide();
    $("div.vali_split").hide();
    $("div.vali_k_folds").hide();
    $("div.Golden_Features").hide();
    $("div.features_selection").hide();
    $("div.start_random_models").hide();
    $("div.hill_climbing_steps").hide();
    $("button.button").hide();
    $("div.self_define").hide();
    $("img.super").hide();
    $("img.unsuper").hide();
    $("img.unsuper2").show();
});
})
//
//====第一段：一開始讓使用者選擇監督非監督以外剩餘功能都藏起來====
$(document).ready(function(){
    $("div.super_mission_type").hide();
    $("div.super_regression_eva").hide();
    $("div.binary_class_eva").hide();
    $("div.multi_class_eva").hide();
    $("div.mode_select").hide();
    $("div.algorithms").hide();
    $("div.ensemble_stacking").hide();
    $("div.validation_strategy").hide();
    $("div.vali_split").hide();
    $("div.vali_k_folds").hide();
    $("div.Golden_Features").hide();
    $("div.features_selection").hide();
    $("div.start_random_models").hide();
    $("div.hill_climbing_steps").hide();
    $("form.unsuper").hide();
    $("button.button").hide();
    $("div.self_define").hide();
    $("img.unsuper2").hide();
});
//====第一段結束=====
//====第二段：使用者點擊監督式學習====
$(document).ready(function(){
$("label.super").click(function(){
    $("div.super_mission_type").show();//任務型態先顯示出來
    $("div.super_regression_eva").show();//因為預設為回歸，故回歸的評價指標一起出來
    $("div.mode_select").show();//模式選擇也可先顯示出來
    $("button.button").show();//因為預設是簡易模式，可讓送出按鈕出現
    $("form.unsuper").hide();
    $("img.unsuper").hide();
    $("img.super").hide();
});
})
//當使用者任務點回歸
$(document).ready(function(){
$("input.regression").click(function(){
    $("div.super_regression_eva").show();
    $("div.binary_class_eva").hide();
    $("div.multi_class_eva").hide();
});
})
//當使用者任務點二元分類
$(document).ready(function(){
$("input.binary").click(function(){
    $("div.super_regression_eva").hide();
    $("div.binary_class_eva").show();
    $("div.multi_class_eva").hide();
});
})
//當使用者任務點多元分類
$(document).ready(function(){
$("input.multi").click(function(){
    $("div.super_regression_eva").hide();
    $("div.binary_class_eva").hide();
    $("div.multi_class_eva").show();
});
})
//====第二段結束=====
//====第三段：使用者點擊自定義模式====
$(document).ready(function(){
$("label.compete").click(function(){
$("div.algorithms").show();
$("div.ensemble_stacking").show();
$("div.validation_strategy").show();
$("div.vali_split").show();//預設是split mode所以這裡要顯示出來
$("div.Golden_Features").show();
$("div.features_selection").show();
$("div.start_random_models").show();
$("div.hill_climbing_steps").show();
$("div.self_define").show();
});
})
//當使用者又點回快速模式時要收回
$(document).ready(function(){
$("label.explain").click(function(){
    $("div.algorithms").hide();
    $("div.ensemble_stacking").hide();
    $("div.validation_strategy").hide();
    $("div.vali_split").hide();
    $("div.vali_k_folds").hide();
    $("div.Golden_Features").hide();
    $("div.features_selection").hide();
    $("div.start_random_models").hide();
    $("div.hill_climbing_steps").hide();
    $("div.self_define").hide();
});
})
//當使用者點擊驗證模式時要做相對切換
$(document).ready(function(){
    $("input.split").click(function(){
    $("div.vali_split").show();
    $("div.vali_k_folds").hide();
    });
})
$(document).ready(function(){
    $("input.kfold").click(function(){
    $("div.vali_split").hide();
    $("div.vali_k_folds").show();
    });
})
//====第三段結束=====

//====220930以下是說明框的呈現=====
function mode() {
    var popup_window = document.getElementById("mode");

    popup_window.style.display = "block";

    window.onclick = function close(e) {
        if (e.target == popup_window) {
            popup_window.style.display = "none";
        }
    }
}
function ensemble() {
    var popup_window = document.getElementById("ensemble");

    popup_window.style.display = "block";

    window.onclick = function close(e) {
        if (e.target == popup_window) {
            popup_window.style.display = "none";
        }
    }
}
function stacking() {
    var popup_window = document.getElementById("stacking");

    popup_window.style.display = "block";

    window.onclick = function close(e) {
        if (e.target == popup_window) {
            popup_window.style.display = "none";
        }
    }
}
function Golden_Features() {
    var popup_window = document.getElementById("Golden_Features");

    popup_window.style.display = "block";

    window.onclick = function close(e) {
        if (e.target == popup_window) {
            popup_window.style.display = "none";
        }
    }
}
function features_selection() {
    var popup_window = document.getElementById("features_selection");

    popup_window.style.display = "block";

    window.onclick = function close(e) {
        if (e.target == popup_window) {
            popup_window.style.display = "none";
        }
    }
}
function start_random_models() {
    var popup_window = document.getElementById("start_random_models");

    popup_window.style.display = "block";

    window.onclick = function close(e) {
        if (e.target == popup_window) {
            popup_window.style.display = "none";
        }
    }
}
function hill_climbing_steps() {
    var popup_window = document.getElementById("hill_climbing_steps");

    popup_window.style.display = "block";

    window.onclick = function close(e) {
        if (e.target == popup_window) {
            popup_window.style.display = "none";
        }
    }
}
$(function() {
    $( document ).tooltip();
  });