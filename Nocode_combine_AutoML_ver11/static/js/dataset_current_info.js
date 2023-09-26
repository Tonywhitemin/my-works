function confirmEvent() {
    if (confirm("請再次確認是否已勾選標籤欄位，若沒有標籤欄位則後續無法使用監督式學習，僅可用非監督式學習") == true) {
      window.event.returnValue=true;
    }
    else {
      window.event.returnValue=false;
    }
}