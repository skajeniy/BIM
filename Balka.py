import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Utility as AllplanUtil
import GeometryValidate as GeometryValidate
from HandleDirection import HandleDirection
from HandleProperties import HandleProperties


print('Load Balka.py')


def check_allplan_version(build_ele, version):
    del build_ele
    del version
    return True


def create_element(build_ele, doc):
    element = Balka(doc)
    return element.create(build_ele)


def move_handle(build_ele, handle_prop, input_pnt, doc):
    build_ele.change_property(handle_prop, input_pnt)
    return create_element(build_ele, doc)


class Balka:

    def __init__(self, doc):
        self.model_ele_list = []
        self.handle_list = []
        self.document = doc

    def create(self, build_ele):
        self.top_part(build_ele)
        self.create_handles(build_ele)
        # self.ref(build_ele);
        return (self.model_ele_list, self.handle_list)

    def bottom_part(self, build_ele):
        brep = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, 0),
                                       AllplanGeo.Vector3D(1, 0, 0),
                                       AllplanGeo.Vector3D(0, 0, 1)),
            build_ele.WidthBottom.value,
            build_ele.Length.value,
            build_ele.HeightBottom.value)

        brep_inter = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0, 0, 0),
                                       AllplanGeo.Vector3D(1, 0, 0),
                                       AllplanGeo.Vector3D(0, 0, 1)),
            build_ele.WidthBottom.value,
            build_ele.Length.value,
            build_ele.HeightBottom.value)

        chamfer_width = build_ele.ChamferBottomTop.value
        chamfer_width_bottom = build_ele.ChamferBottomBottom.value

        if chamfer_width > 0:
            edges = AllplanUtil.VecSizeTList()
            edges.append(1)
            edges.append(3)

            err, brep = AllplanGeo.ChamferCalculus.Calculate(
                brep, edges, chamfer_width, False)

            if not GeometryValidate.polyhedron(err):
                return

        if chamfer_width_bottom > 0:
            edges2 = AllplanUtil.VecSizeTList()
            edges2.append(8)
            edges2.append(10)

            err, brep_inter = AllplanGeo.ChamferCalculus.Calculate(
                brep_inter, edges2, chamfer_width_bottom, False)

            if not GeometryValidate.polyhedron(err):
                return

        err, done_part = AllplanGeo.MakeIntersection(brep, brep_inter)

        return done_part

    def central_part(self, build_ele):
        brep = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(build_ele.WidthBottom.value / 2 - build_ele.CenterWidth.value / 2, 0, build_ele.HeightBottom.value),
                                       AllplanGeo.Vector3D(1, 0, 0),
                                       AllplanGeo.Vector3D(0, 0, 1)),
            build_ele.CenterWidth.value,
            build_ele.Length.value,
            build_ele.CentralHeight.value)

        cone = AllplanGeo.BRep3D.CreateCylinder(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(build_ele.ChamferBottomTop.value, build_ele.Length.value / 8, build_ele.HeightBottom.value + build_ele.CentralHeight.value / 2),
                                       AllplanGeo.Vector3D(0, 0, 1),
                                       AllplanGeo.Vector3D(1, 0, 0)),
            build_ele.Diameter.value /2, build_ele.CenterWidth.value)

        cone1 = AllplanGeo.BRep3D.CreateCylinder(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(build_ele.ChamferBottomTop.value, build_ele.Length.value - build_ele.Length.value / 8, build_ele.HeightBottom.value + build_ele.CentralHeight.value / 2),
                                       AllplanGeo.Vector3D(0, 0, 1),
                                       AllplanGeo.Vector3D(1, 0, 0)),
            build_ele.Diameter.value /2, build_ele.CenterWidth.value)

        err, brep = AllplanGeo.MakeSubtraction(brep, cone)
        err, brep = AllplanGeo.MakeSubtraction(brep, cone1)

        err, done_part = AllplanGeo.MakeUnion(
            brep, self.bottom_part(build_ele))
        return done_part

    def top_part(self, build_ele):
        brep = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(0 - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, 0, build_ele.HeightBottom.value + build_ele.CentralHeight.value),
                                       AllplanGeo.Vector3D(1, 0, 0),
                                       AllplanGeo.Vector3D(0, 0, 1)),
            build_ele.WidthTop.value,
            build_ele.Length.value,
            build_ele.ThicknessTop.value)

        brep_plate = AllplanGeo.BRep3D.CreateCuboid(
            AllplanGeo.AxisPlacement3D(AllplanGeo.Point3D(build_ele.PlateSpace.value - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, 0, build_ele.HeightBottom.value + build_ele.CentralHeight.value + build_ele.ThicknessTop.value),
                                       AllplanGeo.Vector3D(1, 0, 0),
                                       AllplanGeo.Vector3D(0, 0, 1)),
            build_ele.WidthTop.value - build_ele.PlateSpace.value*2,
            build_ele.Length.value,
            build_ele.PlateHeight.value)

        com_prop = AllplanBaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
        com_prop.Pen = 1
        com_prop.Color = build_ele.Color.value

        chamfer_width_top = build_ele.ChamferBottomTop.value

        if chamfer_width_top > 0:
            edges2 = AllplanUtil.VecSizeTList()
            edges2.append(8)
            edges2.append(10)

            err, brep = AllplanGeo.ChamferCalculus.Calculate(
                brep, edges2, chamfer_width_top, False)

            if not GeometryValidate.polyhedron(err):
                return

        err, done_part = AllplanGeo.MakeUnion(
            brep, self.central_part(build_ele))
        err, done_part = AllplanGeo.MakeUnion(done_part, brep_plate)
        self.model_ele_list.append(
            AllplanBasisElements.ModelElement3D(com_prop, done_part))

    def create_handles(self, build_ele):
        h_Height = AllplanGeo.Point3D(
            build_ele.WidthBottom.value / 2, build_ele.Length.value, build_ele.CentralHeight.value + build_ele.HeightBottom.value)
        h_Length = AllplanGeo.Point3D(
            build_ele.WidthBottom.value / 2, 0, build_ele.HeightBottom.value / 2)
        h_WidthBottom = AllplanGeo.Point3D(
            0, build_ele.Length.value, (build_ele.HeightBottom.value - build_ele.ChamferBottomTop.value) / 2)
        h_WidthTop = AllplanGeo.Point3D(
            0 - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.Length.value, build_ele.CentralHeight.value + build_ele.HeightBottom.value + build_ele.ChamferBottomTop.value)
        h_ThicknessTop = AllplanGeo.Point3D(
            build_ele.WidthBottom.value / 2, build_ele.Length.value, build_ele.CentralHeight.value + build_ele.HeightBottom.value - build_ele.HeightBottom.value / 4)
        h_PlateHeight = AllplanGeo.Point3D(
            build_ele.WidthBottom.value / 2, build_ele.Length.value, build_ele.CentralHeight.value + build_ele.HeightBottom.value + build_ele.ThicknessTop.value)
        h_HeightBottom = AllplanGeo.Point3D(
            build_ele.WidthBottom.value / 2, build_ele.Length.value, 0)
        h_CenterWidth = AllplanGeo.Point3D(
            build_ele.WidthBottom.value / 2 - build_ele.CenterWidth.value / 2, build_ele.Length.value, build_ele.CentralHeight.value / 2 + build_ele.HeightBottom.value)

        self.handle_list.append(
            HandleProperties("CentralHeight",
                             AllplanGeo.Point3D(h_Height.X,
                                                h_Height.Y,
                                                h_Height.Z),
                             AllplanGeo.Point3D(h_Height.X,
                                                h_Height.Y,
                                                h_Height.Z - build_ele.CentralHeight.value),
                             [("CentralHeight", HandleDirection.z_dir)],
                             HandleDirection.z_dir,
                             False))

        self.handle_list.append(
            HandleProperties("Length",
                             AllplanGeo.Point3D(h_Length.X,
                                                h_Length.Y + build_ele.Length.value,
                                                h_Length.Z),
                             AllplanGeo.Point3D(h_Length.X,
                                                h_Length.Y,
                                                h_Length.Z),
                             [("Length", HandleDirection.y_dir)],
                             HandleDirection.y_dir,
                             False))

        self.handle_list.append(
            HandleProperties("WidthBottom", AllplanGeo.Point3D(h_WidthBottom.X + build_ele.WidthBottom.value, h_WidthBottom.Y, h_WidthBottom.Z),
                             AllplanGeo.Point3D(
                                 h_WidthBottom.X, h_WidthBottom.Y, h_WidthBottom.Z),
                             [("WidthBottom", HandleDirection.x_dir)],
                             HandleDirection.x_dir,
                             False))

        self.handle_list.append(
            HandleProperties("WidthTop",
                             AllplanGeo.Point3D(h_WidthTop.X + build_ele.WidthTop.value,
                                                h_WidthTop.Y,
                                                h_WidthTop.Z),
                             AllplanGeo.Point3D(h_WidthTop.X,
                                                h_WidthTop.Y,
                                                h_WidthTop.Z),
                             [("WidthTop", HandleDirection.x_dir)],
                             HandleDirection.x_dir,
                             False))

        self.handle_list.append(
            HandleProperties("ThicknessTop",
                             AllplanGeo.Point3D(h_ThicknessTop.X,
                                                h_ThicknessTop.Y,
                                                h_ThicknessTop.Z + build_ele.ThicknessTop.value),
                             AllplanGeo.Point3D(h_ThicknessTop.X,
                                                h_ThicknessTop.Y,
                                                h_ThicknessTop.Z),
                             [("ThicknessTop", HandleDirection.z_dir)],
                             HandleDirection.z_dir,
                             False))

        self.handle_list.append(
            HandleProperties("PlateHeight",
                             AllplanGeo.Point3D(h_PlateHeight.X,
                                                h_PlateHeight.Y,
                                                h_PlateHeight.Z + build_ele.PlateHeight.value),
                             AllplanGeo.Point3D(h_PlateHeight.X,
                                                h_PlateHeight.Y,
                                                h_PlateHeight.Z),
                             [("PlateHeight", HandleDirection.z_dir)],
                             HandleDirection.z_dir,
                             False))

        self.handle_list.append(
            HandleProperties("HeightBottom",
                             AllplanGeo.Point3D(h_HeightBottom.X,
                                                h_HeightBottom.Y,
                                                h_HeightBottom.Z + build_ele.HeightBottom.value),
                             AllplanGeo.Point3D(h_HeightBottom.X,
                                                h_HeightBottom.Y,
                                                h_HeightBottom.Z),
                             [("HeightBottom", HandleDirection.z_dir)],
                             HandleDirection.z_dir,
                             False))

        self.handle_list.append(
            HandleProperties("CenterWidth",
                             AllplanGeo.Point3D(h_CenterWidth.X + build_ele.CenterWidth.value,
                                                h_CenterWidth.Y,
                                                h_CenterWidth.Z),
                             AllplanGeo.Point3D(h_CenterWidth.X,
                                                h_CenterWidth.Y,
                                                h_CenterWidth.Z),
                             [("CenterWidth", HandleDirection.x_dir)],
                             HandleDirection.x_dir,
                             False))
                             
   