import NemAll_Python_Geometry as AllplanGeo
import NemAll_Python_BaseElements as AllplanBaseElements
import NemAll_Python_BasisElements as AllplanBasisElements
import NemAll_Python_Utility as AllplanUtil
import GeometryValidate as GeometryValidate
from HandleDirection import HandleDirection
from HandleProperties import HandleProperties


def check_allplan_version(build_ele, version):
    del build_ele
    del version
    return True


def create_element(build_ele, doc):
    element = Beam(doc)
    return element.create(build_ele)


class Beam:
    ######################################################
    def __init__(self, doc):
        self.model_ele_list = []
        self.handle_list = []
        self.document = doc

    def create(self, build_ele):
        self.connect_all_parts(build_ele)
        self.bottom_beam(build_ele)
        return (self.model_ele_list, self.handle_list)

    def connect_all_parts(self, build_ele):
        com_prop = AllplanBaseElements.CommonProperties()
        com_prop.GetGlobalProperties()
        com_prop.Pen = 1
        com_prop.Color = 3
        com_prop.Stroke = 1
        polyhedron_bottom = self.bottom_beam(build_ele)
        polyhedron_center = self.mid_beam(build_ele)
        polyhedron_top = self.top_beam(build_ele)
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron_bottom, polyhedron_center)
        if err:
            return
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, polyhedron_top)
        if err:
            return 
        self.model_ele_list.append(
            AllplanBasisElements.ModelElement3D(com_prop, polyhedron))

    ######################################################

    def bottom_beam(self, build_ele):
        polyhedron = self.bps(build_ele)
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.bpe21(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.bpe31(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.bpe41(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.bpe22(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.bpe32(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.bpe42(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.bpe23(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.bpe33(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.bpe24(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.bpe34(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.bpf(build_ele))
        return polyhedron
    def mid_beam(self, build_ele):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(0, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(0, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value,
                                        build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, 
                                        build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - (build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value),
                                        build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, 
                                        build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value,
                                         build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, 
                                         build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.Length.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.Length.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - build_ele.LengthTransition.value,
                                        build_ele.LengthBottomCut.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, 
                                        build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value,
                                        build_ele.LengthBottomCut.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, 
                                        build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value,
                                        build_ele.LengthBottomCut.value, 
                                        build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(0, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        path += AllplanGeo.Point3D(0, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        if err:
            return []

        return polyhedron
    def top_beam(self, build_ele):
        polyhedron = self.tps(build_ele)
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.tpe31(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.tpe21(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.tpe31(build_ele, offset=(build_ele.Length.value - build_ele.LengthCenterWidth.value)))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.tpe41(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.tpe22(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.tpe41(build_ele, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2, build_ele.WidthTop.value, 10))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.tpe23(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.tpe42(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.tpe42(build_ele, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2, build_ele.WidthTop.value, 10))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.tpe32(build_ele))
        err, polyhedron = AllplanGeo.MakeUnion(polyhedron, self.tpf(build_ele))
        return polyhedron

    ######################################################

    def tps(self, build_ele):
        base_pol = AllplanGeo.Polygon3D()
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, 
                                        build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                        build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, 
                                        build_ele.WidthTop.value - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2,
                                        build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, 
                                        -(build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2,
                                        build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, 
                                        build_ele.LengthBottomCut.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                        build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base_pol += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, 
                                        build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                        build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, 
                                        build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                        build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, 
                                        build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                        build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        
        err, polyhedron = AllplanGeo.CreatePolyhedron(base_pol, path)

        if err:
            return []

        return polyhedron

    def tpe21(self, build_ele):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - build_ele.LengthTransition.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2 , build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - build_ele.LengthTransition.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2 , build_ele.WidthBottom.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2 + (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.WidthBottom.value + (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value + 10, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - 10, build_ele.HeightBottom.value + build_ele.HeightCenter.value + 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        
        if err:
            return []

        return polyhedron
    def tpe22(self, build_ele):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - build_ele.LengthTransition.value, build_ele.LengthBottomCut.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - build_ele.LengthTransition.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2 - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, -(build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value + 10, build_ele.LengthBottomCut.value + 10, build_ele.HeightBottom.value + build_ele.HeightCenter.value + 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        
        if err:
            return []

        return polyhedron
    def tpe23(self, build_ele):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.WidthBottom.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2 + (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.WidthBottom.value + (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value - 10, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - 10, build_ele.HeightBottom.value + build_ele.HeightCenter.value - 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        
        if err:
            return []

        return polyhedron

    def tpe31(self, build_ele, offset=0):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(offset, build_ele.LengthBottomCut.value,
                                       build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base += AllplanGeo.Point3D(offset, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value,
                                       build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base += AllplanGeo.Point3D(offset, build_ele.WidthBottom.value + (
                    build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2,
                                       build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base += AllplanGeo.Point3D(offset, -(build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2,
                                       build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base += AllplanGeo.Point3D(offset, build_ele.LengthBottomCut.value,
                                       build_ele.HeightBottom.value + build_ele.HeightCenter.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(offset, build_ele.LengthBottomCut.value,
                                   build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        path += AllplanGeo.Point3D(offset + build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value,
                                   build_ele.HeightBottom.value + build_ele.HeightCenter.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        if err:
            return []

        return polyhedron
    def tpe32(self, build_ele):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value, build_ele.LengthBottomCut.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2 - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, -(build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value - 10, build_ele.LengthBottomCut.value + 10, build_ele.HeightBottom.value + build_ele.HeightCenter.value - 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        
        if err:
            return []

        return polyhedron

    def tpe41(self, build_ele, offset1=0, offset2=0, offset3=10):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value,
                                       build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - offset1,
                                       build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value,
                                       build_ele.WidthTop.value - (
                                               build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2 - offset2,
                                       build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - (
                build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                       build_ele.WidthBottom.value + (
                                               build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2 - offset2,
                                       build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value,
                                       build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - offset1,
                                       build_ele.HeightBottom.value + build_ele.HeightCenter.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value,
                                   build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - offset1,
                                   build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value,
                                   build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - offset3 - offset1,
                                   build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        print(base)
        print(path)
        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        if err:
            return []

        return polyhedron
    def tpe42(self, build_ele, offset1=0, offset2=0, offset3=10):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value,
                                       build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - offset1,
                                       build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value + (
                    build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2 - offset2,
                                       build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + (
                    build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                       build_ele.WidthBottom.value + (
                                                   build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2 - offset2,
                                       build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value,
                                       build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - offset1,
                                       build_ele.HeightBottom.value + build_ele.HeightCenter.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value,
                                   build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - offset1,
                                   build_ele.HeightBottom.value + build_ele.HeightCenter.value)
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value,
                                   build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - offset1 - offset3,
                                   build_ele.HeightBottom.value + build_ele.HeightCenter.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        if err:
            return []

        return polyhedron

    def tpf(self, build_ele):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(0, -(build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base += AllplanGeo.Point3D(0, build_ele.WidthTop.value - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        base += AllplanGeo.Point3D(0, build_ele.WidthTop.value - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTop.value)
        base += AllplanGeo.Point3D(0, build_ele.WidthTop.value - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2 - build_ele.Identation.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTop.value)
        base += AllplanGeo.Point3D(0, build_ele.WidthTop.value - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2 - build_ele.Identation.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTop.value + build_ele.HeightPlate.value)
        base += AllplanGeo.Point3D(0, - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2 + build_ele.Identation.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTop.value + build_ele.HeightPlate.value)
        base += AllplanGeo.Point3D(0, - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2 + build_ele.Identation.value, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTop.value)
        base += AllplanGeo.Point3D(0, - (build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTop.value)
        base += AllplanGeo.Point3D(0, -(build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0, -(build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        path += AllplanGeo.Point3D(build_ele.Length.value, -(build_ele.WidthTop.value - build_ele.WidthBottom.value) / 2, build_ele.HeightBottom.value + build_ele.HeightCenter.value + build_ele.HeightTopCut.value)
        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        
        if err:
            return []

        return polyhedron

    ######################################################

    def bps(self, build_ele):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value,
                                    build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                    build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value,
                                    build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2 - build_ele.WidthCentralLittle.value,
                                    build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, 0, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        if err:
            return []

        return polyhedron
    
    def bpe21(self, build_ele):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.WidthBottom.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value - 10 , build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - 10, build_ele.HeightBottom.value - 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        
        if err:
            return []

        return polyhedron
    def bpe22(self, build_ele):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value,
                                       build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value,
                                       build_ele.LengthBottomCut.value + (
                                                   build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                       build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + build_ele.LengthTransition.value + (
                    build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                       (
                                                   build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                       build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + (
                    build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                       0, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value,
                                       build_ele.HeightBottom.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value,
                                   build_ele.HeightBottom.value)
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value - 10, build_ele.LengthBottomCut.value + 10,
                                   build_ele.HeightBottom.value - 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        if err:
            return []

        return polyhedron
    def bpe23(self, build_ele):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value,
                                       build_ele.WidthBottom.value - build_ele.LengthBottomCut.value,
                                       build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(
            build_ele.Length.value - build_ele.LengthCenterWidth.value - build_ele.LengthTransition.value,
            build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - (
                    build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
            build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(
            build_ele.Length.value - build_ele.LengthCenterWidth.value - build_ele.LengthTransition.value - (
                    build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
            build_ele.WidthBottom.value - (
                    build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
            build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - (
                build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                       build_ele.WidthBottom.value,
                                       build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value,
                                       build_ele.WidthBottom.value - build_ele.LengthBottomCut.value,
                                       build_ele.HeightBottom.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value,
                                   build_ele.WidthBottom.value - build_ele.LengthBottomCut.value,
                                   build_ele.HeightBottom.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value + 10,
                                   build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - 10,
                                   build_ele.HeightBottom.value + 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        if err:
            return []

        return polyhedron
    def bpe24(self, build_ele):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value,
                                       build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(
            build_ele.Length.value - build_ele.LengthCenterWidth.value - build_ele.LengthTransition.value,
            build_ele.LengthBottomCut.value + (
                    build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
            build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(
            build_ele.Length.value - build_ele.LengthCenterWidth.value - build_ele.LengthTransition.value - (
                    build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
            (
                    build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
            build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - (
                build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                       0, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value,
                                       build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value,
                                   build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - 10,
                                   build_ele.LengthBottomCut.value + 10, build_ele.HeightBottom.value - 10)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        if err:
            return []

        return polyhedron

    def bpe31(self, build_ele):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(0, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(0, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(0, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(0, 0, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(0, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        
        if err:
            return []

        return polyhedron
    def bpe32(self, build_ele):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, 0, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        path += AllplanGeo.Point3D(build_ele.Length.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        
        if err:
            return []

        return polyhedron
    def bpe33(self, build_ele):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - (build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)


        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - 10, build_ele.HeightBottom.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        
        if err:
            return []

        return polyhedron
    def bpe34(self, build_ele):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value,
                                       build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value, 0,
                                       build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value - (
                    build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                       0, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value,
                                       build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value,
                                   build_ele.LengthBottomCut.value, build_ele.HeightBottom.value)
        path += AllplanGeo.Point3D(build_ele.Length.value - build_ele.LengthCenterWidth.value,
                                   build_ele.LengthBottomCut.value + 10, build_ele.HeightBottom.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        if err:
            return []

        return polyhedron

    def bpe41(self, build_ele):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value,
                                       build_ele.WidthBottom.value - build_ele.LengthBottomCut.value,
                                       build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.WidthBottom.value,
                                       build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + (
                    build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                       build_ele.WidthBottom.value,
                                       build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value,
                                       build_ele.WidthBottom.value - build_ele.LengthBottomCut.value,
                                       build_ele.HeightBottom.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value,
                                   build_ele.WidthBottom.value - build_ele.LengthBottomCut.value,
                                   build_ele.HeightBottom.value)
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value,
                                   build_ele.WidthBottom.value - build_ele.LengthBottomCut.value - 10,
                                   build_ele.HeightBottom.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        if err:
            return []

        return polyhedron
    def bpe42(self, build_ele):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value,
                                       build_ele.HeightBottom.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, 0,
                                       build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value + (
                    build_ele.WidthBottom.value - build_ele.LengthBottomCut.value * 2 - build_ele.WidthCentralLittle.value) / 2,
                                       0, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value,
                                       build_ele.HeightBottom.value)

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value,
                                   build_ele.HeightBottom.value)
        path += AllplanGeo.Point3D(build_ele.LengthCenterWidth.value, build_ele.LengthBottomCut.value + 10,
                                   build_ele.HeightBottom.value)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        if err:
            return []

        return polyhedron

    def bpf(self, build_ele):
        base = AllplanGeo.Polygon3D()
        base += AllplanGeo.Point3D(0, 20, 0)
        base += AllplanGeo.Point3D(0, build_ele.WidthBottom.value - 20, 0)
        base += AllplanGeo.Point3D(0, build_ele.WidthBottom.value, 20)
        base += AllplanGeo.Point3D(0, build_ele.WidthBottom.value, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(0, 0, build_ele.HeightBottom.value - build_ele.HeightBottomCut.value)
        base += AllplanGeo.Point3D(0, 0, 20)
        base += AllplanGeo.Point3D(0, 20, 0)

        if not GeometryValidate.is_valid(base):
            return

        path = AllplanGeo.Polyline3D()
        path += AllplanGeo.Point3D(0, 20, 0)
        path += AllplanGeo.Point3D(build_ele.Length.value,20,0)

        err, polyhedron = AllplanGeo.CreatePolyhedron(base, path)

        
        if err:
            return []

        return polyhedron

    ######################################################