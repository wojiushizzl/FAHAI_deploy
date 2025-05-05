from ultralytics import YOLO

# 导出模型
model = YOLO("yolo11n.pt")

model.export(format="engine")

# 使用TRT模型
trt_model = YOLO("yolo11n.engine")

trt_model.predict("test.jpg", show=True)
