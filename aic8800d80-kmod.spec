# Build an akmod by default. An explicit "kernels" definition makes kmodtool
# build kernel-versioned kmod packages instead.
%global buildforkernels akmod

%global debug_package %{nil}

%global kmod_name aic8800d80
%global repo_name aic8800d80
%global commit f9ab41822373efe70649d011edb587d1170364e7
%global commitdate 20261023
%global shortcommit %(c=%{commit}; echo ${c:0:7})

Name:           %{kmod_name}-kmod
Version:        0.%{commitdate}git%{shortcommit}
Release:        1%{?dist}
Summary:        AIC8800 USB Wi-Fi kernel modules

License:        GPL-2.0-only AND Apache-2.0
URL:            https://github.com/shenmintao/aic8800d80
Source0:        %{url}/archive/%{commit}/%{repo_name}-%{commit}.tar.gz
Source1:        90-aic8800-mode-switch.rules
Source2:        aic8800d80-usb_modeswitch-1111_1111.conf

%global AkmodsBuildRequires gcc, make, elfutils-libelf-devel, xz
BuildRequires:  kmodtool
BuildRequires:  %{AkmodsBuildRequires}
BuildRequires:  systemd-rpm-macros

# kmodtool generates akmod/kmod subpackages and install/check helper macros.
%{expand:%(kmodtool --target %{_target_cpu} --kmodname %{kmod_name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }


%description
Out-of-tree AIC8800 USB Wi-Fi and firmware-loader kernel modules.


%package -n %{pkg_kmod_name}-common
Summary:        Common files for %{kmod_name} kernel modules
License:        GPL-2.0-only
BuildArch:      noarch
Requires:       %{kmod_name}-firmware = %{version}-%{release}
Requires:       util-linux
Requires:       usb_modeswitch


%description -n %{pkg_kmod_name}-common
Common udev integration and USB mode-switch data required by the packaged
%{kmod_name} kernel modules.


%package -n %{kmod_name}-firmware
Summary:        Firmware for AIC8800 USB Wi-Fi/Bluetooth adapters
BuildArch:      noarch


%description -n %{kmod_name}-firmware
Firmware blobs for AIC8800, AIC8800D80, AIC8800D80N, AIC8800D80X2, AIC8800DC,
and AIC8800DLN devices.


%prep
# Error out if kmodtool generated a diagnostic macro.
%{?kmodtool_check}

# Print generated package template for build logs/debugging.
kmodtool --target %{_target_cpu} --kmodname %{kmod_name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null


%setup -q -c

for kernel_version in %{?kernel_versions}; do
    cp -a %{repo_name}-%{commit} _kmod_build_${kernel_version%%___*}
done


%build
for kernel_version in %{?kernel_versions}; do
    kver=${kernel_version%%___*}
    ksrc=${kernel_version##*___}
    make V=1 %{?_smp_mflags} \
        -C "_kmod_build_${kver}/drivers/aic8800" \
        KVER="${kver}" \
        KDIR="${ksrc}" \
        modules
done


%install
install -Dpm0644 %{SOURCE1} \
    %{buildroot}%{_udevrulesdir}/90-aic8800-mode-switch.rules
install -Dpm0644 %{SOURCE2} \
    %{buildroot}%{_datadir}/%{kmod_name}/usb_modeswitch/1111:1111

install -d -m 0755 %{buildroot}%{_prefix}/lib/firmware
cp -r %{repo_name}-%{commit}/fw/aic8800* %{buildroot}%{_prefix}/lib/firmware/

for kernel_version in %{?kernel_versions}; do
    kver=${kernel_version%%___*}
    moddir=%{buildroot}%{kmodinstdir_prefix}/${kver}/%{kmodinstdir_postfix}
    install -d -m 0755 "${moddir}"
    install -Dpm0644 "_kmod_build_${kver}/drivers/aic8800/aic_load_fw/aic_load_fw.ko" "${moddir}/aic_load_fw.ko"
    install -Dpm0644 "_kmod_build_${kver}/drivers/aic8800/aic8800_fdrv/aic8800_fdrv.ko" "${moddir}/aic8800_fdrv.ko"
    install -Dpm0644 "_kmod_build_${kver}/drivers/aic8800/aic_zlp_quirk/aic_zlp_quirk.ko" "${moddir}/aic_zlp_quirk.ko"
done
%{?akmod_install}


%files -n %{pkg_kmod_name}-common
%{_udevrulesdir}/90-aic8800-mode-switch.rules
%dir %{_datadir}/%{kmod_name}
%dir %{_datadir}/%{kmod_name}/usb_modeswitch
%{_datadir}/%{kmod_name}/usb_modeswitch/1111:1111


%files -n %{kmod_name}-firmware
%dir %{_prefix}/lib/firmware/aic8800
%{_prefix}/lib/firmware/aic8800/aic_userconfig.txt
%{_prefix}/lib/firmware/aic8800/fmacfw.bin
%{_prefix}/lib/firmware/aic8800/fmacfw_m2d.bin
%{_prefix}/lib/firmware/aic8800/fmacfw_no_msg_ep.bin
%{_prefix}/lib/firmware/aic8800/fmacfw_no_msg_ep_rf.bin
%{_prefix}/lib/firmware/aic8800/fmacfw_rf.bin
%{_prefix}/lib/firmware/aic8800/fw_adid.bin
%{_prefix}/lib/firmware/aic8800/fw_adid_rf.bin
%{_prefix}/lib/firmware/aic8800/fw_adid_u03.bin
%{_prefix}/lib/firmware/aic8800/fw_ble_scan.bin
%{_prefix}/lib/firmware/aic8800/fw_ble_scan_ad_filter_dcdc.bin
%{_prefix}/lib/firmware/aic8800/fw_ble_scan_ad_filter_ldo.bin
%{_prefix}/lib/firmware/aic8800/fw_patch.bin
%{_prefix}/lib/firmware/aic8800/fw_patch_rf.bin
%{_prefix}/lib/firmware/aic8800/fw_patch_table.bin
%{_prefix}/lib/firmware/aic8800/fw_patch_table_u03.bin
%{_prefix}/lib/firmware/aic8800/fw_patch_u03.bin
%{_prefix}/lib/firmware/aic8800/m2d_ota.bin
%dir %{_prefix}/lib/firmware/aic8800D80
%{_prefix}/lib/firmware/aic8800D80/aic_powerlimit_8800d80.txt
%{_prefix}/lib/firmware/aic8800D80/aic_userconfig_8800d80.txt
%{_prefix}/lib/firmware/aic8800D80/aic_userconfig_8800d80_u11.txt
%{_prefix}/lib/firmware/aic8800D80/aic_userconfig_8800d80_u11_cus.txt
%{_prefix}/lib/firmware/aic8800D80/aic_userconfig_8800d80_u11_pro.txt
%{_prefix}/lib/firmware/aic8800D80/calibmode_8800d80.bin
%{_prefix}/lib/firmware/aic8800D80/fmacfw_8800d80_h_u02.bin
%{_prefix}/lib/firmware/aic8800D80/fmacfw_8800d80_h_u02_ipc.bin
%{_prefix}/lib/firmware/aic8800D80/fmacfw_8800d80_u02.bin
%{_prefix}/lib/firmware/aic8800D80/fmacfw_8800d80_u02_ipc.bin
%{_prefix}/lib/firmware/aic8800D80/fw_adid_8800d80_u02.bin
%{_prefix}/lib/firmware/aic8800D80/fw_ble_scan_ad_filter.bin
%{_prefix}/lib/firmware/aic8800D80/fw_patch_8800d80_u02.bin
%{_prefix}/lib/firmware/aic8800D80/fw_patch_8800d80_u02_ext0.bin
%{_prefix}/lib/firmware/aic8800D80/fw_patch_8800d80_u04.bin
%{_prefix}/lib/firmware/aic8800D80/fw_patch_table_8800d80_u02.bin
%{_prefix}/lib/firmware/aic8800D80/fw_patch_table_8800d80_u04.bin
%{_prefix}/lib/firmware/aic8800D80/lmacfw_rf_8800d80_u02.bin
%dir %{_prefix}/lib/firmware/aic8800D80N
%{_prefix}/lib/firmware/aic8800D80N/aic_powerlimit_8800d80n.txt
%{_prefix}/lib/firmware/aic8800D80N/aic_userconfig_8800d80n.txt
%{_prefix}/lib/firmware/aic8800D80N/fmacfw_btusb_8800d80n_u02.bin
%{_prefix}/lib/firmware/aic8800D80N/fmacfw_calib_8800d80n_u02.bin
%{_prefix}/lib/firmware/aic8800D80N/fmacfw_cinit_8800d80n_u02.bin
%{_prefix}/lib/firmware/aic8800D80N/fmacfw_patch_8800d80n_u02.bin
%{_prefix}/lib/firmware/aic8800D80N/fmacfw_patch_tbl_8800d80n_u02.bin
%{_prefix}/lib/firmware/aic8800D80N/fw_patch_8800d80n_rf_u02.bin
%{_prefix}/lib/firmware/aic8800D80N/fw_patch_8800d80n_rf_u02_ext0.bin
%{_prefix}/lib/firmware/aic8800D80N/fw_patch_8800d80n_u02.bin
%{_prefix}/lib/firmware/aic8800D80N/fw_patch_8800d80n_u02_ext0.bin
%{_prefix}/lib/firmware/aic8800D80N/fw_patch_table_8800d80n_rf_u02.bin
%{_prefix}/lib/firmware/aic8800D80N/fw_patch_table_8800d80n_u02.bin
%{_prefix}/lib/firmware/aic8800D80N/lmacfw_rf_8800d80n.bin
%dir %{_prefix}/lib/firmware/aic8800D80X2
%{_prefix}/lib/firmware/aic8800D80X2/aic_powerlimit_8800d80x2.txt
%{_prefix}/lib/firmware/aic8800D80X2/aic_userconfig_8800d80x2.txt
%{_prefix}/lib/firmware/aic8800D80X2/aicbt.conf
%{_prefix}/lib/firmware/aic8800D80X2/fmacfw_8800d80x2.bin
%{_prefix}/lib/firmware/aic8800D80X2/fw_adid_8800d80x2_u03.bin
%{_prefix}/lib/firmware/aic8800D80X2/fw_adid_8800d80x2_u05.bin
%{_prefix}/lib/firmware/aic8800D80X2/fw_patch_8800d80x2_u03.bin
%{_prefix}/lib/firmware/aic8800D80X2/fw_patch_8800d80x2_u05.bin
%{_prefix}/lib/firmware/aic8800D80X2/fw_patch_8800d80x2_u05_ext0.bin
%{_prefix}/lib/firmware/aic8800D80X2/fw_patch_8800d80x2_u05_ext1.bin
%{_prefix}/lib/firmware/aic8800D80X2/fw_patch_table_8800d80x2_u03.bin
%{_prefix}/lib/firmware/aic8800D80X2/fw_patch_table_8800d80x2_u05.bin
%{_prefix}/lib/firmware/aic8800D80X2/lmacfw_rf_8800d80x2.bin
%dir %{_prefix}/lib/firmware/aic8800DC
%{_prefix}/lib/firmware/aic8800DC/aic_powerlimit_8800dc.txt
%{_prefix}/lib/firmware/aic8800DC/aic_powerlimit_8800dw.txt
%{_prefix}/lib/firmware/aic8800DC/aic_userconfig_8800dc.txt
%{_prefix}/lib/firmware/aic8800DC/aic_userconfig_8800dw.txt
%{_prefix}/lib/firmware/aic8800DC/aic_userconfig_8800dw_u2.txt
%{_prefix}/lib/firmware/aic8800DC/aic_userconfig_8800dw_w311.txt
%{_prefix}/lib/firmware/aic8800DC/fmacfw_calib_8800dc_h_u02.bin
%{_prefix}/lib/firmware/aic8800DC/fmacfw_calib_8800dc_u02.bin
%{_prefix}/lib/firmware/aic8800DC/fmacfw_patch_8800dc_h_u02.bin
%{_prefix}/lib/firmware/aic8800DC/fmacfw_patch_8800dc_ipc_u02.bin
%{_prefix}/lib/firmware/aic8800DC/fmacfw_patch_8800dc_u02.bin
%{_prefix}/lib/firmware/aic8800DC/fmacfw_patch_tbl_8800dc_h_u02.bin
%{_prefix}/lib/firmware/aic8800DC/fmacfw_patch_tbl_8800dc_ipc_u02.bin
%{_prefix}/lib/firmware/aic8800DC/fmacfw_patch_tbl_8800dc_u02.bin
%{_prefix}/lib/firmware/aic8800DC/fw_adid_8800dc_u02.bin
%{_prefix}/lib/firmware/aic8800DC/fw_adid_8800dc_u02h.bin
%{_prefix}/lib/firmware/aic8800DC/fw_patch_8800dc_u02.bin
%{_prefix}/lib/firmware/aic8800DC/fw_patch_8800dc_u02_ext0.bin
%{_prefix}/lib/firmware/aic8800DC/fw_patch_8800dc_u02h.bin
%{_prefix}/lib/firmware/aic8800DC/fw_patch_table_8800dc_u02.bin
%{_prefix}/lib/firmware/aic8800DC/fw_patch_table_8800dc_u02h.bin
%{_prefix}/lib/firmware/aic8800DC/lmacfw_rf_8800dc.bin
%dir %{_prefix}/lib/firmware/aic8800DLN
%{_prefix}/lib/firmware/aic8800DLN/aic_powerlimit_8800dln.txt
%{_prefix}/lib/firmware/aic8800DLN/aic_userconfig_8800dln.txt
%{_prefix}/lib/firmware/aic8800DLN/fmacfw_gaintbl_8800dln.bin
%{_prefix}/lib/firmware/aic8800DLN/fmacfw_initvar_8800dln.bin


%changelog
