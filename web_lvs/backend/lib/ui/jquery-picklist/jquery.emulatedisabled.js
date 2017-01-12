/**
* Emulate Disabled - jQuery plugin for enabling the disabling ;) of select options  for IE
*
* Copyright (c) 2007 George Smith
* Dual licensed under the MIT and GPL licenses:
* http://www.opensource.org/licenses/mit-license.php
* http://www.gnu.org/licenses/gpl.html
*
* Version: 0.1
*/

/**
* Adds disabled option behaviour to a <select> element for IE that can't do it
*
* @usage
* $(select).emulateDisabled(options);
*/
jQuery.fn.emulateDisabled = function() 
{
	return this.each(function()
  {
		// if (jQuery.fn.obviouslyDisabled) jQuery(this).obviouslyDisabled();
		if (jQuery.browser.msie) eDAdd(this);
	});
	function eDRestore(selectBox) 
	{
		jQuery('option', selectBox).each(function()
		{
			if(this.selected && this.disabled)
			{
				this.selected=false;
				if (selectBox.multiple == false) selectBox.selectedIndex = selectBox.selectCurrent;
		}

		});
	}
	function eDAdd(selectBox)
	{
		selectBox.selectCurrent = '';
		jQuery(selectBox).focus(function(){ this.selectCurrent = this.selectedIndex; });
		jQuery(selectBox).change(function(){ eDRestore(this); });
	}
};

jQuery.fn.obviouslyDisabled = function(settings) 
{
 	// set some sensible defaults
	settings = jQuery.extend({
		textColor: 'graytext',
		bgColor: ''
	}, settings);
	return this.each(function() 
	{
		jQuery('option', this).each(function() 
		{
      if (jQuery.browser.msie) {
  			if (this.disabled) 
  			{
  				this.style.color = settings.textColor;
  				this.style.backgroundColor = settings.bgColor;
  			}
  			else
  			{
  				this.style.backgroundColor = "";
  				this.style.color = "";
  			}
      }
		});
		if (jQuery.browser.msie)
		{
      var bg = (this.style.backgroundColor) ? this.style.backgroundColor : '';
      var diff = (bg == '#FFFFFE') ? '#FFFFFF' : '#FFFFFE';
      this.style.backgroundColor = diff;
      this.style.backgroundColor = bg;
    }
	});
};
