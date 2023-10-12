<?php
require '../vendor/autoload.php';

// Get top list
function getTopList($api_key, $limit) {
    $url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest';
    $parameters = [
        'start' => '1',
        'limit' => $limit,
        'sort' => 'market_cap',
        'convert' => 'USD',
    ];
    $headers = [
        'Accepts: application/json',
        'X-CMC_PRO_API_KEY: ' . $api_key,
    ];

    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url . '?' . http_build_query($parameters));
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

    $response = curl_exec($ch);
    curl_close($ch);

    $data = json_decode($response, true);

    if ($data['status']['error_code'] == 0) {
        return $data['data'];
    } else {
        $error_message = $data['status']['error_message'];
        throw new Exception("API request failed. Error: $error_message");
    }
}

// Get OHLC data
function getOHLCData($symbol, $timeframe) {
    $base_url = "https://www.mexc.com/open/api/v2/market/kline?symbol={$symbol}_USDT&interval={$timeframe}m&limit=60";
    $response = file_get_contents($base_url);
    $all_data = json_decode($response, true);

    $ohlc_data_list = [];

    if ($all_data['code'] == 200) {
        foreach ($all_data['data'] as $data_point) {
            $timestamp = $data_point[0];
            $timestamp_datetime = date('Y-m-d H:i:s', $timestamp);
            $close_price = floatval($data_point[2]);
            $high_price = floatval($data_point[3]);
            $low_price = floatval($data_point[4]);

            $ohlc_data_list[] = [$timestamp_datetime, $high_price, $low_price, $close_price];
        }
    } else {
        echo "API request failed with status code: {$all_data['code']}";
        return null;
    }

    return $ohlc_data_list;
}

// Identify supply and demand zones
function identifySupplyDemandZones($data) {
    $min_close = min(array_column($data, 3));
    $max_close = max(array_column($data, 3));
    $demand_zone = array_search($min_close, array_column($data, 3));
    $supply_zone = array_search($max_close, array_column($data, 3));
    
    return [$demand_zone, $supply_zone];
}

// Zigzag function
function zigzag($s, $c = 0.05) {
    $zz = [];
    $signal = 0;
    $inflection = $s[0];

    for ($i = 1; $i < count($s); $i++) {
        // Find first trend
        if ($signal == 0) {
            if ($s[$i] <= ($inflection - $c)) {
                $signal = -1;
            }
            if ($s[$i] >= ($inflection + $c)) {
                $signal = 1;
            }
        }

        // Downtrend, inflection keeps track of the lowest point in the downtrend
        if ($signal == -1) {
            // New Minimum, change inflection
            if ($s[$i] < $inflection) {
                $inflection = $s[$i];
            }
            // Trend Reversal
            if ($s[$i] >= ($inflection + $c)) {
                $signal = 1;
                $zz[] = $inflection;  // Append the lowest point of the downtrend to zz
                $inflection = $s[$i];  // Current point becomes the highest point of the new uptrend
                continue;
            }
        }

        // Uptrend, inflection keeps track of the highest point in the uptrend
        if ($signal == 1) {
            // New Maximum, change inflection
            if ($s[$i] > $inflection) {
                $inflection = $s[$i];
            }
            // Trend Reversal
            if ($s[$i] <= ($inflection - $c)) {
                $signal = -1;
                $zz[] = $inflection;  // Append the highest point of the uptrend to zz
                $inflection = $s[$i];  // Current point becomes the lowest point of the new trend
                continue;
            }
        }
    }
    return $zz;
}

$api_key = '37b4a617-9609-48c6-8a41-d48db5b2ed44';
$limit = 60;
$timeframe = '15';

try {
    $telegram = new \TelegramBot\Api\BotApi('6349402772:AAHU4nMst0YFEyoxaogG5Nmnh8Q_kCQa9qY');
    function send_telegram_message($chatId, $message)
    {
        global $telegram;
        $telegram->sendMessage($chatId, $message, 'HTML');
    }
    $chatId = '5629632710';
    $message = "";

    $top_list = getTopList($api_key, $limit);
    $symbol_list = [];

    foreach ($top_list as $crypto) {
        $symbol = $crypto['symbol'];
        $symbol_list[] = $symbol;
    }

    $zigzag_list = [];
    $supply_list = [];
    $demand_list = [];

    foreach ($symbol_list as $symbol) {
        $ohlc_data_list = getOHLCData($symbol, $timeframe);

        if ($ohlc_data_list) {
            $date_list = array_column($ohlc_data_list, 0);
            $close_price_list = array_column($ohlc_data_list, 3);
            $data = ['Date' => $date_list, 'Close' => $close_price_list];
            $current_price = end($close_price_list);

            // Zigzag
            $s1 = $data['Close'];
            $points = zigzag($s1, 0.0001);

            if (count($points) > 0) {
                $supply_point = $points[0];
                $demand_point = $points[0];

                foreach ($points as $point) {
                    if ($point > $supply_point) {
                        $supply_point = $point;
                    }
                }

                foreach ($points as $point) {
                    if ($point < $demand_point) {
                        $demand_point = $point;
                    }
                }

                if ($current_price <= $demand_point) {
                    echo "The $symbol is in the demand zone\n";
                    $zigzag_list[] = $symbol.'USDT';
                } elseif ($supply_point <= $current_price) {
                    echo "The $symbol is in the supply zone\n";
                    $zigzag_list[] = $symbol.'USDT';
                }
            }

            // Supply and demand zone
            $demand_supply_zones = identifySupplyDemandZones($ohlc_data_list);
            
            if ($demand_supply_zones[0] !== null && $demand_supply_zones[1] !== null) {
                $demand_zone = $demand_supply_zones[0];
                $supply_zone = $demand_supply_zones[1];
            
                if ($current_price <= $ohlc_data_list[$demand_zone][3]) {
                    echo "$symbol: demand zone\n";
                    $demand_list[] = $symbol.'USDT';
                } elseif ($current_price >= $ohlc_data_list[$supply_zone][3]) {
                    echo "$symbol: supply zone\n";
                    $supply_list[] = $symbol.'USDT';
                }
            } else {
                echo "$symbol: Unable to identify supply and demand zones\n";
            }
        }
    }

    $supply_compare_list = array_intersect($zigzag_list, $supply_list);
    $demand_compare_list = array_intersect($zigzag_list, $demand_list);

    if (!empty($supply_compare_list)){
        $message .= "<b>+ </b>: supplyZone: " . implode(', ', $supply_compare_list) . "\n";
    }
    if(!empty($demand_compare_list)){
        $message .= "<i>- </i>: demandZone: " . implode(', ', $demand_compare_list) . "\n";
    }

    // echo "supply_compare_list: " . implode(', ', $supply_compare_list) . "\n";
    // echo "demand_compare_list: " . implode(', ', $demand_compare_list) . "\n";

    if (!empty($message)) {
        send_telegram_message($chatId, $message);   
        var_dump($message);
    }
} catch (Exception $e) {
    echo $e->getMessage() . "\n";
}
?>
