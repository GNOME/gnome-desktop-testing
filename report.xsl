<?xml version="1.0" encoding="ISO-8859-1"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
<xsl:template match="/">
<html>
    <head>
	    <title>
		    GNOME Desktop Tests Report
	    </title>
        <style type="text/css">
    
        body { font:normal 68% verdana,arial,helvetica; color:#000000; }

        h1 { margin: 0px 0px 5px; font: 165% verdana,arial,helvetica }
		h2 { margin-top: 1em; margin-bottom: 0.5em; font: bold 125% verdana,arial,helvetica }
      	h3 { margin-bottom: 0.5em; font: bold 115% verdana,arial,helvetica }
      	h4 { margin-bottom: 0.5em; font: bold 100% verdana,arial,helvetica }
		h5 { margin-bottom: 0.5em; font: bold 100% verdana,arial,helvetica }
		h6 { margin-bottom: 0.5em; font: bold 100% verdana,arial,helvetica }
		
      	table tr th{
        	font-weight: bold;
			font: 80% verdana,arial,helvetica
	        text-align:left;
    	    background:#a6caf0;
      	}
      	table tr td{
       		background:#eeeee0;
            font: 80% verdana,arial,helvetica
      	}
      
		hr.dashed {border: none 0; 
			border-top: 1px dashed #000;
			border-bottom: 1px dashed #ccc;
			width: 95%;
			height: 2px;
			margin: 10px auto 0 0;
			text-align: left;
		}
		hr.clear {border: none 0; 
			border-top: 1px solid #ccc;
			border-bottom: 1px solid #efefef;
			width: 80%;
			height: 2px;
			margin: 10px auto 0 0;
			text-align: left;
		}			
		.passed { color:green;  }
        .failed { font-weight:bold; color:red; }
		.warnings {color:orange;}
		.infos {color:green;}
        </style>
	</head>
	<body>
	    <h1>GNOME Desktop Tests Report</h1>
	    <hr class="clear"></hr>
		<xsl:for-each select="descendant::group">
			<h2>Group Name: <xsl:value-of select="@name"/></h2>
			<table class="details">
			<tr>
				<th>Test Name</th>
				<th>Script Name</th>
				<th>Status</th>
				<th>Time Elapsed (s)</th>
				<th>Error</th>
			</tr>
			<xsl:for-each select="child::script/child::test">
				<tr>
				    <td style="padding: 3px;" align="left" width="40%"><xsl:value-of select="@name"/></td>
					<td><xsl:value-of select="ancestor::script[last()]/@name"/></td>
					<xsl:if test="child::pass/child::text() = 0">
						<td style="padding: 3px;" class="failed" align="right">Failed</td>
					</xsl:if>
					<xsl:if test="child::pass/child::text() = 1">
						<td style="padding: 3px;" class="passed" align="right">Passed</td>
					</xsl:if>
					<td style="padding: 3px;" align="right"><xsl:value-of select="substring-after(COMMENT, 'elapsed_time:')"/></td>
					<td>
						<table>
							<xsl:for-each select="child::CAUSE">
								<tr>
									<td><xsl:value-of select="text()"/></td>
								</tr>
							</xsl:for-each>
						</table>
					</td>
				</tr>
			</xsl:for-each>
			</table>
			<hr class="dashed"></hr>
		</xsl:for-each>
	</body>
</html>
</xsl:template>
</xsl:stylesheet>
