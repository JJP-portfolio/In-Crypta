gdjs.TituloCode = {};
gdjs.TituloCode.localVariables = [];
gdjs.TituloCode.idToCallbackMap = new Map();
gdjs.TituloCode.GDFondoTituloObjects1= [];
gdjs.TituloCode.GDFondoTituloObjects2= [];
gdjs.TituloCode.GDMenu_9595TituloObjects1= [];
gdjs.TituloCode.GDMenu_9595TituloObjects2= [];
gdjs.TituloCode.GDMenu_9595SubObjects1= [];
gdjs.TituloCode.GDMenu_9595SubObjects2= [];
gdjs.TituloCode.GDMenu_9595Op1Objects1= [];
gdjs.TituloCode.GDMenu_9595Op1Objects2= [];
gdjs.TituloCode.GDMenu_9595Op1_9595SubObjects1= [];
gdjs.TituloCode.GDMenu_9595Op1_9595SubObjects2= [];
gdjs.TituloCode.GDMenu_9595Op2Objects1= [];
gdjs.TituloCode.GDMenu_9595Op2Objects2= [];
gdjs.TituloCode.GDMenu_9595Op2_9595SubObjects1= [];
gdjs.TituloCode.GDMenu_9595Op2_9595SubObjects2= [];
gdjs.TituloCode.GDMenu_9595Op3Objects1= [];
gdjs.TituloCode.GDMenu_9595Op3Objects2= [];
gdjs.TituloCode.GDMenu_9595Op3_9595SubObjects1= [];
gdjs.TituloCode.GDMenu_9595Op3_9595SubObjects2= [];
gdjs.TituloCode.GDMenu_9595Op4Objects1= [];
gdjs.TituloCode.GDMenu_9595Op4Objects2= [];
gdjs.TituloCode.GDMenu_9595Op4_9595SubObjects1= [];
gdjs.TituloCode.GDMenu_9595Op4_9595SubObjects2= [];
gdjs.TituloCode.GDMenu_9595AyudaObjects1= [];
gdjs.TituloCode.GDMenu_9595AyudaObjects2= [];


gdjs.TituloCode.mapOfGDgdjs_9546TituloCode_9546GDMenu_95959595Op1Objects1Objects = Hashtable.newFrom({"Menu_Op1": gdjs.TituloCode.GDMenu_9595Op1Objects1});
gdjs.TituloCode.mapOfGDgdjs_9546TituloCode_9546GDMenu_95959595Op2Objects1Objects = Hashtable.newFrom({"Menu_Op2": gdjs.TituloCode.GDMenu_9595Op2Objects1});
gdjs.TituloCode.mapOfGDgdjs_9546TituloCode_9546GDMenu_95959595Op3Objects1Objects = Hashtable.newFrom({"Menu_Op3": gdjs.TituloCode.GDMenu_9595Op3Objects1});
gdjs.TituloCode.mapOfGDgdjs_9546TituloCode_9546GDMenu_95959595Op4Objects1Objects = Hashtable.newFrom({"Menu_Op4": gdjs.TituloCode.GDMenu_9595Op4Objects1});
gdjs.TituloCode.eventsList0 = function(runtimeScene) {

{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.runtimeScene.sceneJustBegins(runtimeScene);
if (isConditionTrue_0) {
{runtimeScene.getScene().getVariables().getFromIndex(0).setNumber(1);
}
{runtimeScene.getGame().getVariables().getFromIndex(0).setNumber(3);
}
{runtimeScene.getGame().getVariables().getFromIndex(1).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(3).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(2).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(4).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(5).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(6).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(7).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(15).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(10).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(11).setNumber(512);
}
{runtimeScene.getGame().getVariables().getFromIndex(12).setNumber(288);
}
{runtimeScene.getGame().getVariables().getFromIndex(13).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(14).setNumber(0);
}
{gdjs.evtTools.camera.setCameraZoom(runtimeScene, 1.25, "", 0);
}
{gdjs.evtTools.camera.setCameraX(runtimeScene, 512, "", 0);
}
{gdjs.evtTools.camera.setCameraY(runtimeScene, 288, "", 0);
}
{gdjs.evtTools.camera.setCameraZoom(runtimeScene, 1, "UI", 0);
}
{gdjs.evtTools.camera.setCameraX(runtimeScene, 640, "UI", 0);
}
{gdjs.evtTools.camera.setCameraY(runtimeScene, 360, "UI", 0);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 1);
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Menu_Op1"), gdjs.TituloCode.GDMenu_9595Op1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Menu_Op2"), gdjs.TituloCode.GDMenu_9595Op2Objects1);
gdjs.copyArray(runtimeScene.getObjects("Menu_Op3"), gdjs.TituloCode.GDMenu_9595Op3Objects1);
gdjs.copyArray(runtimeScene.getObjects("Menu_Op4"), gdjs.TituloCode.GDMenu_9595Op4Objects1);
{for(var i = 0, len = gdjs.TituloCode.GDMenu_9595Op1Objects1.length ;i < len;++i) {
    gdjs.TituloCode.GDMenu_9595Op1Objects1[i].setString(">> 1 · NUEVA PARTIDA <<");
}
}
{for(var i = 0, len = gdjs.TituloCode.GDMenu_9595Op2Objects1.length ;i < len;++i) {
    gdjs.TituloCode.GDMenu_9595Op2Objects1[i].setString("2 · NIVEL 1: CAMPOSANTO");
}
}
{for(var i = 0, len = gdjs.TituloCode.GDMenu_9595Op3Objects1.length ;i < len;++i) {
    gdjs.TituloCode.GDMenu_9595Op3Objects1[i].setString("3 · NIVEL 2: CRIPTA");
}
}
{for(var i = 0, len = gdjs.TituloCode.GDMenu_9595Op4Objects1.length ;i < len;++i) {
    gdjs.TituloCode.GDMenu_9595Op4Objects1[i].setString("4 · SALAS DE PRUEBA");
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 2);
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Menu_Op1"), gdjs.TituloCode.GDMenu_9595Op1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Menu_Op2"), gdjs.TituloCode.GDMenu_9595Op2Objects1);
gdjs.copyArray(runtimeScene.getObjects("Menu_Op3"), gdjs.TituloCode.GDMenu_9595Op3Objects1);
gdjs.copyArray(runtimeScene.getObjects("Menu_Op4"), gdjs.TituloCode.GDMenu_9595Op4Objects1);
{for(var i = 0, len = gdjs.TituloCode.GDMenu_9595Op1Objects1.length ;i < len;++i) {
    gdjs.TituloCode.GDMenu_9595Op1Objects1[i].setString("1 · NUEVA PARTIDA");
}
}
{for(var i = 0, len = gdjs.TituloCode.GDMenu_9595Op2Objects1.length ;i < len;++i) {
    gdjs.TituloCode.GDMenu_9595Op2Objects1[i].setString(">> 2 · NIVEL 1: CAMPOSANTO <<");
}
}
{for(var i = 0, len = gdjs.TituloCode.GDMenu_9595Op3Objects1.length ;i < len;++i) {
    gdjs.TituloCode.GDMenu_9595Op3Objects1[i].setString("3 · NIVEL 2: CRIPTA");
}
}
{for(var i = 0, len = gdjs.TituloCode.GDMenu_9595Op4Objects1.length ;i < len;++i) {
    gdjs.TituloCode.GDMenu_9595Op4Objects1[i].setString("4 · SALAS DE PRUEBA");
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 3);
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Menu_Op1"), gdjs.TituloCode.GDMenu_9595Op1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Menu_Op2"), gdjs.TituloCode.GDMenu_9595Op2Objects1);
gdjs.copyArray(runtimeScene.getObjects("Menu_Op3"), gdjs.TituloCode.GDMenu_9595Op3Objects1);
gdjs.copyArray(runtimeScene.getObjects("Menu_Op4"), gdjs.TituloCode.GDMenu_9595Op4Objects1);
{for(var i = 0, len = gdjs.TituloCode.GDMenu_9595Op1Objects1.length ;i < len;++i) {
    gdjs.TituloCode.GDMenu_9595Op1Objects1[i].setString("1 · NUEVA PARTIDA");
}
}
{for(var i = 0, len = gdjs.TituloCode.GDMenu_9595Op2Objects1.length ;i < len;++i) {
    gdjs.TituloCode.GDMenu_9595Op2Objects1[i].setString("2 · NIVEL 1: CAMPOSANTO");
}
}
{for(var i = 0, len = gdjs.TituloCode.GDMenu_9595Op3Objects1.length ;i < len;++i) {
    gdjs.TituloCode.GDMenu_9595Op3Objects1[i].setString(">> 3 · NIVEL 2: CRIPTA <<");
}
}
{for(var i = 0, len = gdjs.TituloCode.GDMenu_9595Op4Objects1.length ;i < len;++i) {
    gdjs.TituloCode.GDMenu_9595Op4Objects1[i].setString("4 · SALAS DE PRUEBA");
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 4);
}
if (isConditionTrue_0) {
gdjs.copyArray(runtimeScene.getObjects("Menu_Op1"), gdjs.TituloCode.GDMenu_9595Op1Objects1);
gdjs.copyArray(runtimeScene.getObjects("Menu_Op2"), gdjs.TituloCode.GDMenu_9595Op2Objects1);
gdjs.copyArray(runtimeScene.getObjects("Menu_Op3"), gdjs.TituloCode.GDMenu_9595Op3Objects1);
gdjs.copyArray(runtimeScene.getObjects("Menu_Op4"), gdjs.TituloCode.GDMenu_9595Op4Objects1);
{for(var i = 0, len = gdjs.TituloCode.GDMenu_9595Op1Objects1.length ;i < len;++i) {
    gdjs.TituloCode.GDMenu_9595Op1Objects1[i].setString("1 · NUEVA PARTIDA");
}
}
{for(var i = 0, len = gdjs.TituloCode.GDMenu_9595Op2Objects1.length ;i < len;++i) {
    gdjs.TituloCode.GDMenu_9595Op2Objects1[i].setString("2 · NIVEL 1: CAMPOSANTO");
}
}
{for(var i = 0, len = gdjs.TituloCode.GDMenu_9595Op3Objects1.length ;i < len;++i) {
    gdjs.TituloCode.GDMenu_9595Op3Objects1[i].setString("3 · NIVEL 2: CRIPTA");
}
}
{for(var i = 0, len = gdjs.TituloCode.GDMenu_9595Op4Objects1.length ;i < len;++i) {
    gdjs.TituloCode.GDMenu_9595Op4Objects1[i].setString(">> 4 · SALAS DE PRUEBA <<");
}
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Up");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 1);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{runtimeScene.getScene().getVariables().getFromIndex(0).setNumber(4);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Up");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() > 1);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{runtimeScene.getScene().getVariables().getFromIndex(0).sub(1);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Down");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 4);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{runtimeScene.getScene().getVariables().getFromIndex(0).setNumber(1);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Down");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() < 4);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{runtimeScene.getScene().getVariables().getFromIndex(0).add(1);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Return");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Space");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 1);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Tutorial", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Return");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Space");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 2);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Nivel 1", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Return");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Space");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 3);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Nivel 2", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Return");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Space");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
isConditionTrue_0 = false;
{isConditionTrue_0 = (runtimeScene.getScene().getVariables().getFromIndex(0).getAsNumber() == 4);
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Salas", false);
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Menu_Op1"), gdjs.TituloCode.GDMenu_9595Op1Objects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.cursorOnObject(gdjs.TituloCode.mapOfGDgdjs_9546TituloCode_9546GDMenu_95959595Op1Objects1Objects, runtimeScene, true, false);
if (isConditionTrue_0) {
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.isMouseButtonReleased(runtimeScene, "");
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Tutorial", false);
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Menu_Op2"), gdjs.TituloCode.GDMenu_9595Op2Objects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.cursorOnObject(gdjs.TituloCode.mapOfGDgdjs_9546TituloCode_9546GDMenu_95959595Op2Objects1Objects, runtimeScene, true, false);
if (isConditionTrue_0) {
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.isMouseButtonReleased(runtimeScene, "");
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Nivel 1", false);
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Menu_Op3"), gdjs.TituloCode.GDMenu_9595Op3Objects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.cursorOnObject(gdjs.TituloCode.mapOfGDgdjs_9546TituloCode_9546GDMenu_95959595Op3Objects1Objects, runtimeScene, true, false);
if (isConditionTrue_0) {
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.isMouseButtonReleased(runtimeScene, "");
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Nivel 2", false);
}
}

}


{

gdjs.copyArray(runtimeScene.getObjects("Menu_Op4"), gdjs.TituloCode.GDMenu_9595Op4Objects1);

let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.cursorOnObject(gdjs.TituloCode.mapOfGDgdjs_9546TituloCode_9546GDMenu_95959595Op4Objects1Objects, runtimeScene, true, false);
if (isConditionTrue_0) {
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.isMouseButtonReleased(runtimeScene, "");
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Salas", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "u");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "U");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Tutorial", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "t");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "T");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Salas", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Num1");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "1");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Nivel 1", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Num2");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "2");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Nivel 2", false);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
{let isConditionTrue_1 = false;
isConditionTrue_0 = false;
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Num3");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
isConditionTrue_1 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "3");
if(isConditionTrue_1) {
    isConditionTrue_0 = true;
}
}
{
}
}
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Nivel 3", false);
}
}

}


};

gdjs.TituloCode.func = function(runtimeScene) {
runtimeScene.getOnceTriggers().startNewFrame();

gdjs.TituloCode.GDFondoTituloObjects1.length = 0;
gdjs.TituloCode.GDFondoTituloObjects2.length = 0;
gdjs.TituloCode.GDMenu_9595TituloObjects1.length = 0;
gdjs.TituloCode.GDMenu_9595TituloObjects2.length = 0;
gdjs.TituloCode.GDMenu_9595SubObjects1.length = 0;
gdjs.TituloCode.GDMenu_9595SubObjects2.length = 0;
gdjs.TituloCode.GDMenu_9595Op1Objects1.length = 0;
gdjs.TituloCode.GDMenu_9595Op1Objects2.length = 0;
gdjs.TituloCode.GDMenu_9595Op1_9595SubObjects1.length = 0;
gdjs.TituloCode.GDMenu_9595Op1_9595SubObjects2.length = 0;
gdjs.TituloCode.GDMenu_9595Op2Objects1.length = 0;
gdjs.TituloCode.GDMenu_9595Op2Objects2.length = 0;
gdjs.TituloCode.GDMenu_9595Op2_9595SubObjects1.length = 0;
gdjs.TituloCode.GDMenu_9595Op2_9595SubObjects2.length = 0;
gdjs.TituloCode.GDMenu_9595Op3Objects1.length = 0;
gdjs.TituloCode.GDMenu_9595Op3Objects2.length = 0;
gdjs.TituloCode.GDMenu_9595Op3_9595SubObjects1.length = 0;
gdjs.TituloCode.GDMenu_9595Op3_9595SubObjects2.length = 0;
gdjs.TituloCode.GDMenu_9595Op4Objects1.length = 0;
gdjs.TituloCode.GDMenu_9595Op4Objects2.length = 0;
gdjs.TituloCode.GDMenu_9595Op4_9595SubObjects1.length = 0;
gdjs.TituloCode.GDMenu_9595Op4_9595SubObjects2.length = 0;
gdjs.TituloCode.GDMenu_9595AyudaObjects1.length = 0;
gdjs.TituloCode.GDMenu_9595AyudaObjects2.length = 0;

gdjs.TituloCode.eventsList0(runtimeScene);
gdjs.TituloCode.GDFondoTituloObjects1.length = 0;
gdjs.TituloCode.GDFondoTituloObjects2.length = 0;
gdjs.TituloCode.GDMenu_9595TituloObjects1.length = 0;
gdjs.TituloCode.GDMenu_9595TituloObjects2.length = 0;
gdjs.TituloCode.GDMenu_9595SubObjects1.length = 0;
gdjs.TituloCode.GDMenu_9595SubObjects2.length = 0;
gdjs.TituloCode.GDMenu_9595Op1Objects1.length = 0;
gdjs.TituloCode.GDMenu_9595Op1Objects2.length = 0;
gdjs.TituloCode.GDMenu_9595Op1_9595SubObjects1.length = 0;
gdjs.TituloCode.GDMenu_9595Op1_9595SubObjects2.length = 0;
gdjs.TituloCode.GDMenu_9595Op2Objects1.length = 0;
gdjs.TituloCode.GDMenu_9595Op2Objects2.length = 0;
gdjs.TituloCode.GDMenu_9595Op2_9595SubObjects1.length = 0;
gdjs.TituloCode.GDMenu_9595Op2_9595SubObjects2.length = 0;
gdjs.TituloCode.GDMenu_9595Op3Objects1.length = 0;
gdjs.TituloCode.GDMenu_9595Op3Objects2.length = 0;
gdjs.TituloCode.GDMenu_9595Op3_9595SubObjects1.length = 0;
gdjs.TituloCode.GDMenu_9595Op3_9595SubObjects2.length = 0;
gdjs.TituloCode.GDMenu_9595Op4Objects1.length = 0;
gdjs.TituloCode.GDMenu_9595Op4Objects2.length = 0;
gdjs.TituloCode.GDMenu_9595Op4_9595SubObjects1.length = 0;
gdjs.TituloCode.GDMenu_9595Op4_9595SubObjects2.length = 0;
gdjs.TituloCode.GDMenu_9595AyudaObjects1.length = 0;
gdjs.TituloCode.GDMenu_9595AyudaObjects2.length = 0;


return;

}

gdjs['TituloCode'] = gdjs.TituloCode;
