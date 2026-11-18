* Five-transistor OTA in SkyWater SKY130 (sky130_fd_pr), placed with RNL 0.4
* .include "sky130_fd_pr_stub.spice"
XM1 x inp tail 0 sky130_fd_pr__nfet_01v8 w=4 l=0.15
XM2 out inn tail 0 sky130_fd_pr__nfet_01v8 w=4 l=0.15
XM3 x x vdd vdd sky130_fd_pr__pfet_01v8 w=8 l=0.15
XM4 out x vdd vdd sky130_fd_pr__pfet_01v8 w=8 l=0.15
XM5 tail bias 0 0 sky130_fd_pr__nfet_01v8 w=8 l=0.5
XM6 bias bias 0 0 sky130_fd_pr__nfet_01v8 w=8 l=0.5
Ib vdd bias 20u
XCL out 0 sky130_fd_pr__cap_mim_m3_1 w=10 l=10
Vdd vdd 0 1.8
* @RNL(type="header") {
*   @VERSION("0.4");
*   @USE-PACKAGE(name="rnl-std-all", version="0.4");
*   @USE-PACKAGE(name="pdk-sky130", version="0.3")
* }
* @RNL {
*   &vdd @ADD-TO $SUPPLY_NET_SET;
*   # @SELECT-INSTANCE(model="sky130_fd_pr__*fet*", recursive=true) => @TEXT("W/L=${w}/${l}", key="model", valign="top");
*   #XCL @TEXT("${w}\times{}${l} \mu{}m^{2}", key="value");
*
*   %dp = #XM1(left) #XM2(right) #XM5(tail) @AS $DIFFERENTIAL_PAIR_N;
*   %cm = {#XM3}(ref) {#XM4}(out) @AS $CURRENT_MIRROR_P;
*
*   %jd = (-8, 4); %jg = (-2, 8); %jo = (8, 4); %jc = (18, 4); %jt = (0, -5);
*   %jb = (-22, -5); %j6 = (-14, -8);
*   &x @WIRE {#XM3:d %jd #XM1:d};
*   &x @WIRE {#XM3:g %jg #XM4:g};
*   &x @WIRE(mode="horizontal-vertical") {%jd %jg};
*   &out @WIRE {#XM4:d %jo #XM2:d};
*   &tail @WIRE(mode="vertical-horizontal") {#XM1:s %jt};
*   &tail @WIRE(mode="vertical-horizontal") {#XM2:s %jt};
*   &tail @WIRE {%jt #XM5:d};
*   &bias @WIRE {#Ib:n %jb #XM6:d};
*   &bias @WIRE {#XM6:g %j6 #XM5:g};
*   &bias @WIRE(mode="vertical-horizontal") {%j6 %jb};
*   $JUNCTION @ATTACH %jd => @PLACE(-8, 4);
*   $JUNCTION @ATTACH %jg => @PLACE(-2, 8);
*   $JUNCTION @ATTACH %jo => @PLACE(8, 4);
*   $JUNCTION @ATTACH %jc => @PLACE(18, 4);
*   $JUNCTION @ATTACH %jt => @PLACE(0, -5);
*   $JUNCTION @ATTACH %jb => @PLACE(-22, -5);
*   $JUNCTION @ATTACH %j6 => @PLACE(-14, -8);
*
*   %pi = $NET_LABEL @ATTACH &inp;
*   $NET_LABEL @ATTACH &inn => @ORIENT("MY") => %pn;
*   $NET_LABEL @ATTACH &out => @ORIENT("MY") => %po;
*   &inp @WIRE {%pi::pin #XM1:g};
*   &inn @WIRE {%pn::pin #XM2:g};
*   &out @WIRE {%jo %jc %po::pin};
*   &out @WIRE {%jc #XCL:c0}
* }
* @RNL(type="generated", priority="high") {
*   #XM1 @PLACE(-8, 0); #XM2 @PLACE(8, 0) => @ORIENT("MY");
*   #XM3 @PLACE(-8, 8) => @ORIENT("MY"); #XM4 @PLACE(8, 8);
*   #XM5 @PLACE(0, -8); #XM6 @PLACE(-22, -8) => @ORIENT("MY"); #Ib @PLACE(-22, 0);
*   #XCL @PLACE(18, 1); #Vdd @PLACE(30, 4);
*   %pi @PLACE(-13, 0); %pn @PLACE(13, 0); %po @PLACE(23, 4);
*   %nl_XM1_b = $NET_LABEL_STUB @ATTACH #XM1:b; %nl_XM1_b::l @PLACE(-8, 0) => @ORIENT("MY");
*   %nl_XM2_b = $NET_LABEL_STUB @ATTACH #XM2:b; %nl_XM2_b::l @PLACE(8, 0) => @ORIENT("R0");
*   %gs_XM5_s = $GROUND_STUB @ATTACH #XM5:s; %gs_XM5_s::g @PLACE(0, -12);
*   %nl_XM5_b = $NET_LABEL_STUB @ATTACH #XM5:b; %nl_XM5_b::l @PLACE(0, -8) => @ORIENT("MY");
*   %gs_XM6_s = $GROUND_STUB @ATTACH #XM6:s; %gs_XM6_s::g @PLACE(-22, -12);
*   %nl_XM6_b = $NET_LABEL_STUB @ATTACH #XM6:b; %nl_XM6_b::l @PLACE(-22, -8) => @ORIENT("R0");
*   %gs_XCL_c1 = $GROUND_STUB @ATTACH #XCL:c1; %gs_XCL_c1::g @PLACE(18, -3);
*   %gs_Vdd_n = $GROUND_STUB @ATTACH #Vdd:n; %gs_Vdd_n::g @PLACE(30, -1);
*   %ss_XM3_s = $SUPPLY_STUB @ATTACH #XM3:s; %ss_XM3_s::s @PLACE(-8, 12);
*   %nl_XM3_b = $NET_LABEL_STUB @ATTACH #XM3:b; %nl_XM3_b::l @PLACE(-8, 8) => @ORIENT("R0");
*   %ss_XM4_s = $SUPPLY_STUB @ATTACH #XM4:s; %ss_XM4_s::s @PLACE(8, 12);
*   %nl_XM4_b = $NET_LABEL_STUB @ATTACH #XM4:b; %nl_XM4_b::l @PLACE(8, 8) => @ORIENT("MY");
*   %ss_Ib_p = $SUPPLY_STUB @ATTACH #Ib:p; %ss_Ib_p::s @PLACE(-22, 5);
*   %ss_Vdd_p = $SUPPLY_STUB @ATTACH #Vdd:p; %ss_Vdd_p::s @PLACE(30, 9)
* }
.end
