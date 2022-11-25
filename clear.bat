@echo off
@rem 清理日志
del unpack.log.*
type nul > unpack.log
@rem 清理报告
type nul > report.txt
@rem 清理密码表
type nul > passwords.txt
echo clear ok!
pause
echo on