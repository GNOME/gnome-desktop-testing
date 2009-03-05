<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en" dir="ltr">
      <head>
        <title>
    GNOME LDTP Tests Report
    </title>
        <!-- Launchpad style sheet -->
        <style type="text/css" media="screen, print">@import url(https://edge.launchpad.net/+icing/rev7667/+style-slimmer.css);</style>
        <!--[if lte IE 7]>
      <style type="text/css">#lp-apps span {margin: 0 0.125%;}</style>
    <![endif]-->
        <style type="text/css">
      fieldset.collapsed div, fieldset div.collapsed {display: none;}
    </style>
        <noscript>
          <style type="text/css">
        fieldset.collapsible div, fieldset div.collapsed {display: block;}
      </style>
        </noscript>
        <script type="text/javascript" src="https://edge.launchpad.net/+icing/build/launchpad.js"/>
        <script type="text/javascript">var cookie_scope = '; Path=/; Secure; Domain=.launchpad.net';</script>
        <script type="text/javascript">
      function onLoadFunction() {
        sortables_init();
        initInlineHelp();
      }
      registerLaunchpadFunction(onLoadFunction);
    </script>
        <link rel="shortcut icon" href="https://edge.launchpad.net/@@/launchpad.png"/>
      </head>
      <body id="document" class="tab-bugs onecolumn">
        <div id="mainarea">
          <div id="container">
            <!--[if IE 7]>&nbsp;<![endif]-->
            <div id="navigation-tabs">
                          
                          
                        </div>
            <div>
              <p>
                <br/>
              </p>
              <h1>GNOME LDTP Tests Report</h1>
              <p>
                  This are the results from a run of GNOME Desktop Tests. <br/>
                  If you find false positives, please, report bugs against <a href="https://launchpad.net/gnome-desktop-testing/+filebug">gnome-desktop-testing</a> project.
              </p>
              <table width="100%" class="sortable listing" id="trackers">
                <thead>
                  <tr>
                    <th>Test Name</th>
                    <th>Script Name</th>
                    <th>Status</th>
                    <th>Time Elapsed (s)</th>
                    <th>Error</th>
                    <th>Screenshot</th>
                  </tr>
                </thead>
                <tbody>
                  <xsl:for-each select="descendant::group">
                    <xsl:for-each select="child::script/child::test">
                      <tr>
                        <td>
                          <xsl:value-of select="@name"/>
                        </td>
                        <td>
                          <xsl:value-of select="ancestor::script[last()]/@name"/>
                        </td>
                        <xsl:choose>
                          <xsl:when test="child::pass/child::text() = 0">
                            <td><font color="red">Failed</font></td>
                          </xsl:when>
                          <xsl:otherwise>
                            <td><font color="green">Passed</font></td>
                          </xsl:otherwise>
                        </xsl:choose>
                        <td>
                            <xsl:value-of select="child::time/child::text()"/>
                        </td>
                        <td>
                          <xsl:if test="child::pass/child::text() = 0">
                              <xsl:value-of select="child::error/child::text()"/>
                          </xsl:if>
                        </td>
                        <td>
                          <xsl:if test="child::pass/child::text() = 0">
                            <xsl:apply-templates select="child::screenshot" mode="link"/>
                          </xsl:if>
                        </td>
                      </tr>
                    </xsl:for-each>
                  </xsl:for-each>
                </tbody>
              </table>
              <p>
                <!-- *** Last Paragraph Space *** -->
              </p>
            </div>
            <div class="clear"/>
          </div>
          <!--id="container"-->
        </div>
        <!--id="mainarea"-->
       <div id="help-pane" class="invisible">
          <div id="help-body">
            <iframe id="help-pane-content" class="invisible" src="javascript:void(0);"/>
          </div>
          <div id="help-footer">
            <span id="help-close"/>
          </div>
        </div>
      </body>
    </html>
  </xsl:template>
  <xsl:template match="screenshot" mode="link">
    <a href="{text()}">
      <xsl:value-of select="text()"/>
    </a>
    <xsl:text> </xsl:text>
  </xsl:template>
</xsl:stylesheet>
