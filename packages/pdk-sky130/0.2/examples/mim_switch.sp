* Switched-capacitor sampling network with MIM capacitors, CMOS switches, and ESD diode in SkyWater SKY130
* .include "sky130_fd_pr_stub.spice"
XD1 0 vin sky130_fd_pr__diode_pw2nd_05v5 area=1e12
XMN1 vin clk vsamp 0 sky130_fd_pr__nfet_01v8_lvt w=2 l=0.15
XMP1 vsamp clkb vin vdd sky130_fd_pr__pfet_01v8_lvt w=4 l=0.15
XC1 vsamp vbot sky130_fd_pr__cap_mim_m3_1 w=10 l=10
XMN2 vbot rst 0 0 sky130_fd_pr__nfet_05v0_nvt w=2 l=0.9
XC2 vsamp 0 sky130_fd_pr__cap_mim_m3_2 w=4 l=4
Vdd vdd 0 1.8
* @RNL(type="header") {
*   @VERSION("0.4");
*   @USE-PACKAGE(name="rnl-std-all", version="0.4");
*   @USE-PACKAGE(name="pdk-sky130", version="0.2")
* }
* @RNL {
*   &vdd @ADD-TO $SUPPLY_NET_SET;
*   # @SELECT-INSTANCE(model="sky130_fd_pr__*fet*", recursive=true) => @TEXT("W/L=${w}/${l}", key="model");
*   # @SELECT-INSTANCE(model="sky130_fd_pr__cap_mim_*", recursive=true) => @TEXT("${w}\times{}${l} \mu{}m^{2}", key="value");
*   #XD1 @TEXT("A=${area}", key="value");
*
*   /* the CMOS switch: vin on the bus above, vsamp on the bus below, the bulks between */
*   %jin = (-18, 4); %jn = (-8, 4); %jp = (8, 4);
*   %jsn = (-8, -4); %jsp = (8, -4); %js1 = (12, -4); %js2 = (20, -4);
*   &vin @WIRE {%p_vin::pin %jin %jn %jp #XMP1:s};
*   &vin @WIRE {%jin #XD1:k};
*   &vin @WIRE {%jn #XMN1:d};
*   &vsamp @WIRE {#XMN1:s %jsn %jsp %js1 %js2 %p_out::pin};
*   &vsamp @WIRE {#XMP1:d %jsp};
*   &vsamp @WIRE {%js1 #XC1:c0};
*   &vsamp @WIRE {%js2 #XC2:c0};
*   &vbot @WIRE {#XC1:c1 #XMN2:d};
*   $JUNCTION @ATTACH %jin => @PLACE(-18, 4);
*   $JUNCTION @ATTACH %jn => @PLACE(-8, 4);
*   $JUNCTION @ATTACH %jsp => @PLACE(8, -4);
*   $JUNCTION @ATTACH %js1 => @PLACE(12, -4);
*   $JUNCTION @ATTACH %js2 => @PLACE(20, -4);
*
*   %p_vin = $NET_LABEL @ATTACH &vin;
*   %p_clk = $NET_LABEL @ATTACH &clk;
*   $NET_LABEL @ATTACH &clkb => @ORIENT("MY") => %p_clkb;
*   %p_rst = $NET_LABEL @ATTACH &rst;
*   $NET_LABEL @ATTACH &vsamp => @ORIENT("MY") => %p_out;
*   &clk @WIRE {%p_clk::pin #XMN1:g};
*   &clkb @WIRE {#XMP1:g %p_clkb::pin};
*   &rst @WIRE {%p_rst::pin #XMN2:g}
* }
* @RNL(type="generated", priority="high") {
*   #XD1 @PLACE(-18, 0) => @ORIENT("R180");
*   #XMN1 @PLACE(-8, 0); #XMP1 @PLACE(8, 0) => @ORIENT("MY");
*   #XC1 @PLACE(12, -7); #XMN2 @PLACE(12, -12);
*   #XC2 @PLACE(20, -7); #Vdd @PLACE(30, 2);
*   %p_vin @PLACE(-22, 4); %p_clk @PLACE(-13, 0); %p_clkb @PLACE(14, 0);
*   %p_rst @PLACE(7, -12); %p_out @PLACE(24, -4);
*   %gs_XD1_a = $GROUND_STUB @ATTACH(gap=2) #XD1:a; %gs_XD1_a::g @PLACE(-18, -4);
*   %gs_XMN1_b = $GROUND_STUB @ATTACH(gap=2) #XMN1:b; %gs_XMN1_b::g @PLACE(-1, 0);
*   %ss_XMP1_b = $SUPPLY_STUB @ATTACH(gap=2) #XMP1:b; %ss_XMP1_b::s @PLACE(1, 0);
*   %gs_XMN2_s = $GROUND_STUB @ATTACH(gap=2) #XMN2:s; %gs_XMN2_s::g @PLACE(12, -16);
*   %gs_XMN2_b = $GROUND_STUB @ATTACH(gap=2) #XMN2:b; %gs_XMN2_b::g @PLACE(14, -15);
*   %gs_XC2_c1 = $GROUND_STUB @ATTACH(gap=2) #XC2:c1; %gs_XC2_c1::g @PLACE(20, -11);
*   %gs_Vdd_n = $GROUND_STUB @ATTACH(gap=2) #Vdd:n; %gs_Vdd_n::g @PLACE(30, -3);
*   %ss_Vdd_p = $SUPPLY_STUB @ATTACH(gap=2) #Vdd:p; %ss_Vdd_p::s @PLACE(30, 7)
* }
.end
