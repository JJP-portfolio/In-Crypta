gdjs.TituloCode = {};
gdjs.TituloCode.localVariables = [];
gdjs.TituloCode.idToCallbackMap = new Map();
gdjs.TituloCode.GDFondoTituloObjects1= [];
gdjs.TituloCode.GDFondoTituloObjects2= [];


gdjs.TituloCode.eventsList0 = function(runtimeScene) {

{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.runtimeScene.sceneJustBegins(runtimeScene);
if (isConditionTrue_0) {
{runtimeScene.getGame().getVariables().getFromIndex(0).setNumber(3);
}
{runtimeScene.getGame().getVariables().getFromIndex(1).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(3).setNumber(0);
}
{runtimeScene.getGame().getVariables().getFromIndex(2).setNumber(0);
}
{gdjs.evtTools.camera.setCameraZoom(runtimeScene, 2, "", 0);
}
{gdjs.evtTools.camera.setCameraX(runtimeScene, 480, "", 0);
}
{gdjs.evtTools.camera.setCameraY(runtimeScene, 270, "", 0);
}
{gdjs.evtTools.camera.setCameraZoom(runtimeScene, 2, "UI", 0);
}
{gdjs.evtTools.camera.setCameraX(runtimeScene, 480, "UI", 0);
}
{gdjs.evtTools.camera.setCameraY(runtimeScene, 270, "UI", 0);
}
}

}


{


let isConditionTrue_0 = false;
isConditionTrue_0 = false;
isConditionTrue_0 = gdjs.evtTools.input.wasKeyJustPressed(runtimeScene, "Return");
if (isConditionTrue_0) {
{gdjs.evtTools.sound.playSound(runtimeScene, "SFX_UI", false, 100, 1);
}
{gdjs.evtTools.runtimeScene.replaceScene(runtimeScene, "Nivel 1", false);
}
}

}


};

gdjs.TituloCode.func = function(runtimeScene) {
runtimeScene.getOnceTriggers().startNewFrame();

gdjs.TituloCode.GDFondoTituloObjects1.length = 0;
gdjs.TituloCode.GDFondoTituloObjects2.length = 0;

gdjs.TituloCode.eventsList0(runtimeScene);
gdjs.TituloCode.GDFondoTituloObjects1.length = 0;
gdjs.TituloCode.GDFondoTituloObjects2.length = 0;


return;

}

gdjs['TituloCode'] = gdjs.TituloCode;
