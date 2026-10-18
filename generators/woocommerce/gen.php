<?php
// Driver for PDF Invoices & Packing Slips for WooCommerce 5.16.4 (run with: wp eval-file gen.php)
// env: N (carts per file), SYN (ubl|cii), OUT (output dir), CARTS (comma list of carts_*.json), ROUND_SUB (yes|no)
$N=(int)getenv('N'); $OUT=getenv('OUT'); @mkdir("$OUT/cii",0777,true); @mkdir("$OUT/ubl",0777,true);
update_option('woocommerce_default_country','DE:BE'); update_option('woocommerce_currency','EUR');
update_option('woocommerce_calc_taxes','yes'); update_option('woocommerce_prices_include_tax','yes');
update_option('woocommerce_tax_based_on','base'); update_option('woocommerce_tax_round_at_subtotal',getenv('ROUND_SUB')?:'no');
update_option('woocommerce_price_num_decimals','2');
update_option('woocommerce_store_address','Hauptstr. 1'); update_option('woocommerce_store_city','Berlin'); update_option('woocommerce_store_postcode','10115');
global $wpdb;
if(!$wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->prefix}woocommerce_tax_rates")){
  WC_Tax::_insert_tax_rate(['tax_rate_country'=>'DE','tax_rate'=>'19.0000','tax_rate_name'=>'MwSt 19','tax_rate_priority'=>1,'tax_rate_shipping'=>1,'tax_rate_class'=>'']);
  WC_Tax::_insert_tax_rate(['tax_rate_country'=>'DE','tax_rate'=>'7.0000','tax_rate_name'=>'MwSt 7','tax_rate_priority'=>1,'tax_rate_shipping'=>0,'tax_rate_class'=>'reduced-rate']);
}
update_option('wpo_ips_edi_settings',['enabled'=>'1','syntax'=>getenv('SYN'),'ubl_format'=>'peppol-bis-3p0','cii_format'=>'factur-x-1p0']);
update_option('wpo_ips_edi_tax_settings',['class'=>['standard'=>['category'=>'S','scheme'=>'VAT','reason'=>'none'],'reduced-rate'=>['category'=>'S','scheme'=>'VAT','reason'=>'none']]]);
$g=get_option('wpo_wcpdf_settings_general',[]); $g['vat_number']='DE123456788'; $g['shop_name']=['default'=>'Shop DE GmbH']; $g['shop_address_line_1']='Hauptstr. 1'; $g['shop_address_city']='Berlin'; $g['shop_address_postcode']='10115'; $g['shop_address_country']='DE'; update_option('wpo_wcpdf_settings_general',$g);
$is=get_option('wpo_wcpdf_documents_settings_invoice',[]); $is['enabled']=1; update_option('wpo_wcpdf_documents_settings_invoice',$is);
$prod=[];
function product($price,$rate){ global $prod; $k="$price|$rate"; if(isset($prod[$k])) return $prod[$k];
  $p=new WC_Product_Simple(); $p->set_name("P $k"); $p->set_regular_price($price); $p->set_tax_class($rate=='7'?'reduced-rate':''); $p->save(); return $prod[$k]=$p; }
$rows=[];
foreach(explode(',',getenv('CARTS')) as $path){
 foreach(array_slice(json_decode(file_get_contents($path),true),0,$N) as $c){
  $o=wc_create_order(); $o->set_currency('EUR'); $o->set_prices_include_tax(true);
  $o->set_billing_company('Kunde AG'); $o->set_billing_first_name('Max'); $o->set_billing_last_name('M'); $o->set_billing_address_1('Marktplatz 5'); $o->set_billing_city('München'); $o->set_billing_postcode('80331'); $o->set_billing_country('DE'); $o->set_billing_email('ap@kunde.example');
  $o->update_meta_data('_billing_vat_number','DE811907980');
  foreach($c['lines'] as $l){ $o->add_product(product($l['unit_gross'],$l['rate']),$l['qty']); }
  if((float)$c['ship']>0){ $s=new WC_Order_Item_Shipping(); $s->set_method_title('Versand'); $s->set_method_id('flat_rate'); $s->set_total(round((float)$c['ship']/1.19,2)); $o->add_item($s); }
  $o->calculate_totals(true);
  if((float)$c['pct']>0){ $code='pct'.(int)$c['pct']; if(!wc_get_coupon_id_by_code($code)){ $cp=new WC_Coupon(); $cp->set_code($code); $cp->set_discount_type('percent'); $cp->set_amount((float)$c['pct']); $cp->save(); } $o->apply_coupon($code); }
  $o->set_status('completed'); $o->save();
  wpo_ips_edi_save_order_taxes($o);
  $doc=wcpdf_get_invoice($o,true);
  $xml=wpo_ips_edi_write_file($doc,false,true);
  $syn=getenv('SYN'); $tag=($syn=='ubl'?'bis3':'fx').'-rs'.(getenv('ROUND_SUB')?:'no');
  $fn="wcpdf5164-$tag"."__".$c['id'].".xml"; file_put_contents("$OUT/$syn/$fn",$xml);
  $rows[]=['id'=>$c['id'],'woo_total'=>$o->get_total(),'shop_paid'=>$c['paid'],'file'=>$fn];
 }
}
file_put_contents("$OUT/gen_".getenv('SYN').'_'.(getenv('ROUND_SUB')?:'no').".json",json_encode($rows,JSON_PRETTY_PRINT)); echo "DONE ".count($rows)."\n";
