// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface IStakedUSDeOFT {
    function deposit(uint256 assets, address receiver) external returns (uint256);
    function convertToAssets(uint256 shares) external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
}
