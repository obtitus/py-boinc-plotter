
# This file is part of the py-boinc-plotter,
# which provides parsing and plotting of boinc statistics and
# badge information.
# Copyright (C) 2013 obtitus@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# END LICENCE
import os
thisFolder = os.path.abspath(os.path.dirname(__file__))
dataFolder = os.path.join(thisFolder, 'data')

boinccmd = os.path.join(dataFolder, 'boinccmd.out')
html_worldcommunitygrid = os.path.join(dataFolder, 
                                       'httpwwwworldcommunitygridorgmsviewBoincResultsdofilterDevice0filterStatus1projectId1pageNum1sortBysentTime.html')
xml_worldcommunitygrid = os.path.join(dataFolder, 
                                      'httpwwwworldcommunitygridorgverifyMemberdonametulluscode5bff34a7261500fd219a28a85bf8fa84.xml')

html_yoyo = os.path.join(dataFolder, 'httpwwwrechenkraftnetyoyoresultsphpuserid34278offset0show_names1state0appid.html')
html_primegrid = os.path.join(dataFolder, 'httpwwwprimegridcomresultsphpuserid222267offset0show_names1state0appid.html')

project_rosetta = """<project>
    <master_url>http://boinc.bakerlab.org/rosetta/</master_url>
    <project_name>rosetta@home</project_name>
    <symstore></symstore>
    <user_name>tullus</user_name>
    <team_name>UserFriendly.org</team_name>
    <host_venue></host_venue>
    <email_hash>5cb5683c94d51078f78a7b2c597ef687</email_hash>
    <cross_project_id>b1927da537aca0ca6bfc8c6e3355ec5b</cross_project_id>
    <cpid_time>1366480421.000000</cpid_time>
    <user_total_credit>2542.768740</user_total_credit>
    <user_expavg_credit>227.387611</user_expavg_credit>
    <user_create_time>1366480421.000000</user_create_time>
    <rpc_seqno>25</rpc_seqno>
    <userid>0</userid>
    <teamid>0</teamid>
    <hostid>1611639</hostid>
    <host_total_credit>2542.768740</host_total_credit>
    <host_expavg_credit>227.387672</host_expavg_credit>
    <host_create_time>1366480434.000000</host_create_time>
    <nrpc_failures>0</nrpc_failures>
    <master_fetch_failures>0</master_fetch_failures>
    <min_rpc_time>1366708725.998005</min_rpc_time>
    <next_rpc_time>0.000000</next_rpc_time>
    <rec>4.375081</rec>
    <rec_time>1371936970.144788</rec_time>
    <resource_share>100.000000</resource_share>
    <desired_disk_usage>0.000000</desired_disk_usage>
    <duration_correction_factor>0.848538</duration_correction_factor>
    <sched_rpc_pending>0</sched_rpc_pending>
    <send_time_stats_log>0</send_time_stats_log>
    <send_job_log>0</send_job_log>
    <verify_files_on_app_start/>
    <dont_request_more_work/>
    <rsc_backoff_time>
        <name>CPU</name>
        <value>0.000000</value>
    </rsc_backoff_time>
    <rsc_backoff_interval>
        <name>CPU</name>
        <value>0.000000</value>
    </rsc_backoff_interval>
<gui_urls>


    <gui_url>
        <name>FoldIt!</name>
        <description>Want to play a game?</description>
        <url>http://fold.it</url>
    </gui_url>
    <gui_url>
        <name>Science of Rosetta</name>
        <description>An overview of the basic science behind Rosetta@home</description>
        <url>http://boinc.bakerlab.org/rosetta/rah_education/</url>
    </gui_url>
    <gui_url>
        <name>Message boards</name>
        <description>Correspond with other users on the Rosetta@home message boards</description>
        <url>http://boinc.bakerlab.org/rosetta/forum_index.php</url>
    </gui_url>
    <ifteam>
        <gui_url>
            <name>Team</name>
            <description>Info about UserFriendly.org</description>
            <url>http://boinc.bakerlab.org/rosetta/team_display.php?teamid=5857</url>
        </gui_url>
    </ifteam>
</gui_urls>
    <sched_priority>-0.000000</sched_priority>
    <last_rpc_time>0.000000</last_rpc_time>
    <project_files_downloaded_time>0.000000</project_files_downloaded_time>
</project>
"""

project_worldcommunitygrid = """
<project>
    <master_url>http://www.worldcommunitygrid.org/</master_url>
    <project_name>World Community Grid</project_name>
    <symstore></symstore>
    <user_name>Tullus</user_name>
    <team_name>UserFriendly.Org</team_name>
    <host_venue></host_venue>
    <email_hash>5cb5683c94d51078f78a7b2c597ef687</email_hash>
    <cross_project_id>b1927da537aca0ca6bfc8c6e3355ec5b</cross_project_id>
    <cpid_time>1226653035.000000</cpid_time>
    <user_total_credit>213009.258971</user_total_credit>
    <user_expavg_credit>1769.796739</user_expavg_credit>
    <user_create_time>1226653035.000000</user_create_time>
    <rpc_seqno>235</rpc_seqno>
    <userid>537977</userid>
    <teamid>7233</teamid>
    <hostid>1919469</hostid>
    <host_total_credit>207377.622169</host_total_credit>
    <host_expavg_credit>1769.166557</host_expavg_credit>
    <host_create_time>1330703048.000000</host_create_time>
    <nrpc_failures>0</nrpc_failures>
    <master_fetch_failures>0</master_fetch_failures>
    <min_rpc_time>1371929458.471207</min_rpc_time>
    <next_rpc_time>1372188637.471207</next_rpc_time>
    <rec>2310.814492</rec>
    <rec_time>1371965386.915625</rec_time>
    <resource_share>100.000000</resource_share>
    <desired_disk_usage>0.000000</desired_disk_usage>
    <duration_correction_factor>1.000000</duration_correction_factor>
    <sched_rpc_pending>0</sched_rpc_pending>
    <send_time_stats_log>0</send_time_stats_log>
    <send_job_log>0</send_job_log>
    <dont_use_dcf/>
    <rsc_backoff_time>
        <name>CPU</name>
        <value>0.000000</value>
    </rsc_backoff_time>
    <rsc_backoff_interval>
        <name>CPU</name>
        <value>0.000000</value>
    </rsc_backoff_interval>
<gui_urls>

   <gui_url>
      <name>Research Overview</name>
      <description>Learn about the projects hosted at World Community Grid</description>
      <url>http://www.worldcommunitygrid.org/research/viewAllProjects.do</url>
   </gui_url>
   <gui_url>
      <name>News and Updates</name>
      <description>The latest information about World Community Grid and its research projects</description>
      <url>http://www.worldcommunitygrid.org/about_us/displayNews.do</url>
   </gui_url>
   <gui_url>
      <name>My Grid</name>
      <description>Your statistics and settings</description>
      <url>http://www.worldcommunitygrid.org/ms/viewMyMemberPage.do</url>
   </gui_url>
   <gui_url>
      <name>Results Status</name>
      <description>View the status of your assigned work</description>
      <url>http://www.worldcommunitygrid.org/ms/viewBoincResults.do</url>
   </gui_url>
   <gui_url>
      <name>Device Profiles</name>
      <description>Update your device settings</description>
      <url>http://www.worldcommunitygrid.org/ms/device/viewProfiles.do</url>
   </gui_url>
   <gui_url>
      <name>Forums</name>
      <description>Visit the World Community Grid forums</description>
      <url>http://www.worldcommunitygrid.org/forumLogin.do</url>
   </gui_url>
   <gui_url>
      <name>Help</name>
      <description>Search for help in our help system</description>
      <url>http://www.worldcommunitygrid.org/help/viewHelp.do</url>
   </gui_url>
</gui_urls>
    <sched_priority>-1.029408</sched_priority>
    <last_rpc_time>1371929437.471207</last_rpc_time>
    <project_files_downloaded_time>0.000000</project_files_downloaded_time>
</project>
"""

task_active = """<result>
    <name>faah41423_ZINC08270033_xBr27_refmac2_A_PR_03_0</name>
    <wu_name>faah41423_ZINC08270033_xBr27_refmac2_A_PR_03</wu_name>
    <version_num>715</version_num>
    <plan_class></plan_class>
    <project_url>http://www.worldcommunitygrid.org/</project_url>
    <final_cpu_time>0.000000</final_cpu_time>
    <final_elapsed_time>0.000000</final_elapsed_time>
    <exit_status>0</exit_status>
    <state>2</state>
    <report_deadline>1372752295.000000</report_deadline>
    <received_time>1371888297.544660</received_time>
    <estimated_cpu_time_remaining>14328.936352</estimated_cpu_time_remaining>
<active_task>
    <active_task_state>1</active_task_state>
    <app_version_num>715</app_version_num>
    <slot>5</slot>
    <pid>96072</pid>
    <scheduler_state>2</scheduler_state>
    <checkpoint_cpu_time>12200.950000</checkpoint_cpu_time>
    <fraction_done>0.514148</fraction_done>
    <current_cpu_time>12867.580000</current_cpu_time>
    <elapsed_time>12883.982196</elapsed_time>
    <swap_size>2781458432.000000</swap_size>
    <working_set_size>173539328.000000</working_set_size>
    <working_set_size_smoothed>173539328.000000</working_set_size_smoothed>
    <page_fault_rate>0.000000</page_fault_rate>
   <graphics_exec_path>/Library/Application Support/BOINC Data/projects/www.worldcommunitygrid.org/wcgrid_faah_graphics_prod_darwin_64.x86.7.15</graphics_exec_path>
   <slot_path>/Library/Application Support/BOINC Data/slots/5</slot_path>
</active_task>
</result>
"""

workunit = """<workunit>
    <name>faah42091_ZINC58026222_xBr27_refmac2_A_PR_01</name>
    <app_name>faah</app_name>
    <version_num>715</version_num>
    <rsc_fpops_est>50657828504791.000000</rsc_fpops_est>
    <rsc_fpops_bound>1013156570095820.000000</rsc_fpops_bound>
    <rsc_memory_bound>125000000.000000</rsc_memory_bound>
    <rsc_disk_bound>314572800.000000</rsc_disk_bound>
    <command_line>
-dpf faah42091_ZINC58026222_xBr27_refmac2_A_P_01.dpf -gpf ZINC58026222_xBr27_refmac2_A_P_01.gpf -seed 303113325
    </command_line>
    <file_ref>
        <file_name>f5357a2639947fe9a1f6f5eed56b12e5.dpf.gzb</file_name>
        <open_name>./faah42091_ZINC58026222_xBr27_refmac2_A_P_01.dpf</open_name>
    </file_ref>
    <file_ref>
        <file_name>faah42091_ZINC58026222_xBr27_refmac2_A_PR_01_AD4.1_bound.dat.gzb</file_name>
        <open_name>./AD4.1_bound.dat</open_name>
    </file_ref>
    <file_ref>
        <file_name>faah42091_ZINC58026222_xBr27_refmac2_A_PR_01_ZINC58026222.pdbqt.gzb</file_name>
        <open_name>./ZINC58026222.pdbqt</open_name>
    </file_ref>
    <file_ref>
        <file_name>faah.xBr27_refmac2_A_PR.pdbqt.gzb</file_name>
        <open_name>./xBr27_refmac2_A_PR.pdbqt</open_name>
    </file_ref>
    <file_ref>
        <file_name>deee9691f8d8188cde3e25dce3d0e540.gpf.gzb</file_name>
        <open_name>./ZINC58026222_xBr27_refmac2_A_P_01.gpf</open_name>
    </file_ref>
    <file_ref>
        <file_name>faah.protease.dat.gzb</file_name>
        <open_name>./protease.dat</open_name>
    </file_ref>
</workunit>
"""

workunit_suspended = """<result>
    <name>pps_sr2sieve_62184531_0</name>
    <wu_name>pps_sr2sieve_62184531</wu_name>
    <version_num>139</version_num>
    <plan_class>cpuPPSsieve</plan_class>
    <project_url>http://www.primegrid.com/</project_url>
    <final_cpu_time>34120.610000</final_cpu_time>
    <final_elapsed_time>34173.498170</final_elapsed_time>
    <exit_status>0</exit_status>
    <state>2</state>
    <report_deadline>1373525048.000000</report_deadline>
    <received_time>1373006649.350320</received_time>
    <estimated_cpu_time_remaining>339590.472511</estimated_cpu_time_remaining>
<active_task>
    <active_task_state>9</active_task_state>
    <app_version_num>139</app_version_num>
    <slot>16</slot>
    <pid>8725</pid>
    <scheduler_state>1</scheduler_state>
    <checkpoint_cpu_time>44714.330000</checkpoint_cpu_time>
    <fraction_done>0.307364</fraction_done>
    <current_cpu_time>44714.430000</current_cpu_time>
    <elapsed_time>44846.073217</elapsed_time>
    <swap_size>2782945280.000000</swap_size>
    <working_set_size>206282752.000000</working_set_size>
    <working_set_size_smoothed>206282752.000122</working_set_size_smoothed>
    <page_fault_rate>0.000000</page_fault_rate>
</active_task>
</result>
"""

workunit_running = """<result>
<name>DSFL_00100-37_0000046_0555_1</name>
<wu_name>DSFL_00100-37_0000046_0555</wu_name>
<version_num>625</version_num>
<plan_class></plan_class>
<project_url>http://www.worldcommunitygrid.org/</project_url>
<final_cpu_time>0.000000</final_cpu_time>
<final_elapsed_time>0.000000</final_elapsed_time>
<exit_status>0</exit_status>
<state>2</state>
<report_deadline>1373310023.000000</report_deadline>
<received_time>1372446024.959453</received_time>
<estimated_cpu_time_remaining>2060.234200</estimated_cpu_time_remaining>
<active_task>
<active_task_state>1</active_task_state>
<app_version_num>625</app_version_num>
<slot>5</slot>
<pid>7130</pid>
<scheduler_state>2</scheduler_state>
<checkpoint_cpu_time>11916.430000</checkpoint_cpu_time>
<fraction_done>0.883333</fraction_done>
<current_cpu_time>12429.430000</current_cpu_time>
<elapsed_time>12566.508714</elapsed_time>
<swap_size>2591920128.000000</swap_size>
<working_set_size>54267904.000000</working_set_size>
<working_set_size_smoothed>54262111.801669</working_set_size_smoothed>
<page_fault_rate>0.000000</page_fault_rate>
<graphics_exec_path>/Library/Application Support/BOINC Data/projects/www.worldcommunitygrid.org/wcgrid_dsfl_gfx_prod_darwin_64.x86.6.25</graphics_exec_path>
<slot_path>/Library/Application Support/BOINC Data/slots/5</slot_path>
</active_task>"""

workunit_ready_to_run = """<result> 
<name>faah41856_ZINC09836600_xBr27_refmac2_A_PR_02_0</name>
<wu_name>faah41856_ZINC09836600_xBr27_refmac2_A_PR_02</wu_name>
<version_num>715</version_num> 
<plan_class></plan_class>
<project_url>http://www.worldcommunitygrid.org/</project_url>
<final_cpu_time>0.000000</final_cpu_time>
<final_elapsed_time>0.000000</final_elapsed_time>
<exit_status>0</exit_status> 
<state>2</state> 
<report_deadline>1373310023.000000</report_deadline> 
<received_time>1372446024.959453</received_time> 
<estimated_cpu_time_remaining>28329.146516</estimated_cpu_time_remaining>"""

application="""<app>
    <name>faah</name>
    <user_friendly_name>FightAIDS@Home</user_friendly_name>
    <non_cpu_intensive>0</non_cpu_intensive>
</app>"""
