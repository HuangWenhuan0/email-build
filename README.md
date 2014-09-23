#BuildApk Usage：

1、python makezip.py - [create mbuild.zip in output directory]

2、copy mbuild.zip to ../AndroidMail project directory

3、python mbuild.zip - [print help information]
	
	Usage:   
	  mbuild <command> [options]

	Commands:
	  ant                         Ant Build Android Project
	  gradle                      Gradle Build Android Project
	  ant-batch                   Ant Batch Build Android Project
	  gradle-batch                Gradle Batch Build Android Project

	General Options:
	  -h, --help                Show help.
	  -V, --version             Show version and exit.
	  -v, --verbose             Give me more output. Option is additive, and can
								be used up to 3 times.
	  -d, --download-url <url>  Base URL of Build Configuration (default
								http://42.62.42.75:51866/build-conf2/)

4、python mbuild.zip ant         - [ant build]

5、python mbuild.zip gradle      - [gradle build]
	Parameter List：
		Build Options:
		  -c, --channel <channel>     use specified channel.
		  -g, --debug                 android apk is debug or release, (release is
									  default value).
		  -p, --package-name <package_name>
									  use new package name to build android project.
		  --branch-name <branchname>  specify branch name (not null)
		  -b, --enable-branch-name    enable branch name as application name.
		  --display-name <display name>
									  specify display name when the apk is installed.
		  --version-name <version name>
									  specify app version name
									  (android:versionName="").
		  --version-code <version code>
									  specify app version code
									  (android:versionCode="").
		  --db-version-code <version code>
									  specify app dbVersionCode (<meta-data
									  android:name="db_versionCode",
									  android:value="").
		  --apk-prefix <apk prefix>   specify apk prefix name (default is WpsMail).
		  --hash-types <hash algorithms>
									  apk hash algorithms list (default "md5,sha1")
		  --apk-name-format <apk name format>
									  specify apk prefix name (default is
									  %prefix_%channel_%versionName_%commitId)
									  --apk-name-format option controls the apk name.
									  The only valid option is:
									  %prefix         apk-prefix
									  %channel        app channel
									  %versionName    app version name
									  %versionCode    app version code
									  %commitId       git commit sha1
									  %dbVersoinCode  app dbversionCode
									  %packageName    app package name

		General Options:
		  -h, --help                  Show help.
		  -V, --version               Show version and exit.
		  -v, --verbose               Give me more output. Option is additive, and can
									  be used up to 3 times.
		  -d, --download-url <url>    Base URL of Build Configuration (default
									  http://42.62.42.75:51866/build-conf2/)
	

6、python mbuild.zip ant-batch       - [ant batch build]

7、python mbuild.zip gradle-batch    - [gradle batch build]
	
	与单包构建相比，只有一个参数不同-C, --batch-channel
	该参数控制指定APP的渠道号[<meta-data android:name="channel" android:value="渠道号" />]
	参数格式：
		[channel-prefix],[channel-number-length],[number-range]
		channel-prefix:         表示渠道号前缀
		channel-number-length:  表示渠道号数字部分的总位数，如果不足此位数，在左边以0填充
		number-range:           表示渠道数字部分的范围
		
		注：中间以逗号隔开，参数之间不能留有空格
		
		以c,4,1-15为例，生成的渠道号为
		c0001, c0002, c0003, c0004, ……, c0014, c0015
		
	
	Parameter List：
		Batch Build Options:
		  -g, --debug                 android apk is debug or release, (release is
									  default value).
		  -C, --batch-channel <batch_channel>
									  use specified channel (default is c,3,1-70).
		  -p, --package-name <package_name>
									  use new package name to build android project.
		  --branch-name <branchname>  specify branch name (not null)
		  -b, --enable-branch-name    enable branch name as application name.
		  --display-name <display name>
									  specify display name when the apk is installed.
		  --version-name <version name>
									  specify app version name
									  (android:versionName="").
		  --version-code <version code>
									  specify app version code
									  (android:versionCode="").
		  --db-version-code <version code>
									  specify app dbVersionCode (<meta-data
									  android:name="db_versionCode",
									  android:value="").
		  --apk-prefix <apk prefix>   specify apk prefix name (default is WpsMail).
		  --hash-types <hash algorithms>
									  apk hash algorithms list (default "md5,sha1")
		  --apk-name-format <apk name format>
									  specify apk prefix name (default is
									  %prefix_%channel_%versionName_%commitId)
									  --apk-name-format option controls the apk name.
									  The only valid option is:
									  %prefix         apk-prefix
									  %channel        app channel
									  %versionName    app version name
									  %versionCode    app version code
									  %commitId       git commit sha1
									  %dbVersoinCode  app dbversionCode
									  %packageName    app package name

		General Options:
		  -h, --help                  Show help.
		  -V, --version               Show version and exit.
		  -v, --verbose               Give me more output. Option is additive, and can
									  be used up to 3 times.
		  -d, --download-url <url>    Base URL of Build Configuration (default
									  http://42.62.42.75:51866/build-conf2/)

    
    
        