# aic8800d80-kmod

Fedora RPM package for https://github.com/shenmintao/aic8800d80

Out-of-tree AIC8800 USB Wi-Fi and firmware-loader kernel modules.


## How to build

```bash
# 1. Dowload the source tarball.
spectool -g aic8800d80-kmod.spec

# 2. Build the *.src.rpm
mock  --buildsrpm --sources . --spec aic8800d80-kmod.spec
cp /var/lib/mock/*/result/aic8800d80-kmod-*.src.rpm ./

# 3. Build *.rpm
mock --rebuild ./aic8800d80-kmod-*.src.rpm

# 4. Find built *.rpm
ls -lah /var/lib/mock/*/result/*.rpm
```
